import type { BlockBlobUploadResponse, ContainerClient } from "@azure/storage-blob";
import { BlobServiceClient } from "@azure/storage-blob";
import { v4 as uuidv4 } from "uuid";
import dotenv from "dotenv";

dotenv.config();

function connectToStorageAccount(): ContainerClient {
    const connectionString = process.env.STORAGE_ACCOUNT_CONNECTION_STRING;
    if (!connectionString) 
        throw new Error("No connection string provided");
    const blobServiceClient = BlobServiceClient.fromConnectionString(connectionString);
    return blobServiceClient.getContainerClient("input");
}

async function generateAndUploadFile(containerClient: ReturnType<typeof connectToStorageAccount>) {
    const folderPath = `${new Date().getFullYear()}/${new Date().getMonth() + 1}`;
    const timestamp = new Date().getTime();
    const appendices = getRandomAppendix();
    const awaitPromises: Promise<BlockBlobUploadResponse>[] = appendices.map(async (appendix) => {
        const fileName = `order-${timestamp}-${appendix}.json`;
        const fileContent = { id: uuidv4(), data: "random data" };
        const blockBlobClient = containerClient.getBlockBlobClient(`${folderPath}/${fileName}`);
        return blockBlobClient.upload(JSON.stringify(fileContent), JSON.stringify(fileContent).length);
    });
    await Promise.all(awaitPromises);
}

function getRandomAppendix(): string[] {
    const randomFactor = Math.random();
    if (randomFactor < 0.9) {
        return ["a", "b"];
    } else if (randomFactor < 0.95) {
        return ["a"];
    } else {
        return ["b"];
    }
}

async function main() {
    const containerClient = connectToStorageAccount();

    for (let i = 0; i < 1000; i++) {
        await generateAndUploadFile(containerClient);
    }
}

main().catch((error) => {
    console.error("Error uploading files:", error);
});
