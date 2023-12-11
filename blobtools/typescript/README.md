# What can blob index tags be used for?

This is an example repository that shows how to implement an even oriented saga pattern, supperted with blob index tags, blob leases and runs essentially for almost no costs on Azure.

## Step 1: Create many pair of blobs, but sometimes it's missing part A and sometimes part B.
## Step 2: These blobs are uploaded to a storage account
## Step 3: An event grid subscription pushed events to a storage queue
## Step 4: The Storage Queue gets read by a process who does this:
### 4.1: Check if the blob has a lease, if not, acquire a lease. If it has a lease, skip this blob.
### 4.2: Get the tags of the blob, if it hasn't a tag, add 