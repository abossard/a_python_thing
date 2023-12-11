type EncryptedSaga = {
    encrypted_blob_url: string;
    encrypted_key_url: string;
    status: 'missing_key' | 'missing_blob' | 'success' | 'error';
}