import { BlobServiceClient } from "@azure/storage-blob";
import { QueueServiceClient } from "@azure/storage-queue";
import dotenv from "dotenv";
/*
 STEP 1:
 Reads from queues and looks of both blobs are there. The pair is formed by the file name, 
 which is the same for both blobs, and the suffix, which is either "a" or "b".

 If both blobs are found, all the relevant information is sent to the output queue.

*/
dotenv.config();

type ProcessResult = {
    status: "success" | "missing" | "error" | "ignore";
    message: string | null;
    subjects: string[] | null;
}

const containerName = "input";
const connectionString = process.env.STORAGE_ACCOUNT_CONNECTION_STRING;
if (!connectionString)
    throw new Error("No connection string provided");
const inputQueueName = "step1";
const outputQueueName = "step2";

const blobServiceClient = BlobServiceClient.fromConnectionString(connectionString);
const containerClient = blobServiceClient.getContainerClient(containerName);

async function processQueueMessage(message: any): Promise<ProcessResult> {
    const content = JSON.parse(base64Decode(message.messageText));
    if (!content.type.toLowerCase().includes("blob")) {
        console.log("Not a blob created event");
        return { status: "ignore", message: `Event is of type: ${content.type} and not Blob Event`, subjects: null };
    }
    const rawBlobUrl = content.subject; // is like: "/blobServices/default/containers/input/blobs/2023/11/order-1701284315287-a.json"
    const blobUrl = rawBlobUrl.replace(/.*\/blobs\//, "");
    const blobName = blobUrl.substring(blobUrl.lastIndexOf("/") + 1);
    const fileName = blobName.substring(0, blobName.lastIndexOf("."));
    const suffix = fileName.charAt(fileName.length - 1);

    let alternateSuffix: string;
    if (suffix === "a") {
        alternateSuffix = "b";
    } else if (suffix === "b") {
        alternateSuffix = "a";
    } else {
        console.log("Invalid suffix");
        return { status: "ignore", message: `Invalid suffix: ${suffix}`, subjects: null };
    }

    const alternateFileName = blobUrl.replace(fileName, fileName.slice(0, -1) + alternateSuffix);
    const alternateBlobClient = containerClient.getBlobClient(alternateFileName);
    const alternateBlobExists = await alternateBlobClient.exists();

    if (alternateBlobExists) {
        console.log("Found alternate blob");
        return { status: "success", message: `found alternate blob ${alternateFileName}`, subjects: fileName };
    } else {
        console.log("Did not find alternate blob");
        return { status: "missing", message: `did not find alternate blob ${alternateFileName}`, subjects: fileName };
    }
}

function base64Decode(encodedString: string): string {
    const buffer = Buffer.from(encodedString, 'base64');
    return buffer.toString('utf-8');
}

// make an async main
async function main(connectionString: string, inputQueue: string, outputQueue: string) {
    // get the queue client
    const blobServiceClient = BlobServiceClient.fromConnectionString(connectionString);
    const queueServiceClient = QueueServiceClient.fromConnectionString(connectionString);
    const inputQueueClient = queueServiceClient.getQueueClient(inputQueue);
    const outputQueueClient = queueServiceClient.getQueueClient(outputQueue);
    console.log('Starting to process queue messages')
    while (true) {
        const response = await inputQueueClient.receiveMessages({ numberOfMessages: 10 });
        if (response.receivedMessageItems.length === 0) {
            console.log('No messages left to process')
            break;
        }
        console.log(`Processing ${response.receivedMessageItems.length} messages`)
        const messages = response.receivedMessageItems;
        await Promise.all(messages.map(async (message) => {
            const processResult = await processQueueMessage(message);
            console.log(processResult);
            const status = processResult.status;
            

            if (status === "success")
            {
                if(processResult.subjects) {
                    await outputQueueClient.sendMessage(JSON.stringify(processResult.subjects));
                } else {
                    console.error("No subject provided in ProcessResult", processResult);
                }
            }

            if(processResult.status === "missing") {
                // add blob index tags on the subject
                if(processResult.subjects) {
                    for (const subject of processResult.subjects) {
                        const blobIndexTag = subject;
                        const blobUrl = subject;
                        const blobClient = containerClient.getBlobClient(blobUrl);
                        await blobClient.setTags({ blobIndexTag });
                    }
                } else {
                    console.error("No subject provided in ProcessResult", processResult);
                }
            }
            await inputQueueClient.deleteMessage(message.messageId, message.popReceipt);
        }));
        console.log(`Processed ${response.receivedMessageItems.length} messages.`)
    }
}

// call the main
main(connectionString, inputQueueName, outputQueueName).catch((error) => {
    console.error("Error processing queue message:", error);
});
