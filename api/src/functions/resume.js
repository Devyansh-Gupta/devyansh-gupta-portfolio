// GET /api/resume — mint a short-lived, read-only, single-blob service SAS
// and 302-redirect the visitor to Azure Blob Storage.
// Per Microsoft SAS best practices: least privilege (read, one blob),
// short expiry, HTTPS-only. Account key lives only in app settings.
const { app } = require('@azure/functions');
const {
  BlobServiceClient, StorageSharedKeyCredential,
  generateBlobSASQueryParameters, BlobSASPermissions, SASProtocol,
} = require('@azure/storage-blob');

const EXPIRY_MINUTES = Number(process.env.RESUME_SAS_MINUTES || 10);

app.http('resume', {
  route: 'resume',
  methods: ['GET'],
  authLevel: 'anonymous',
  handler: async (request, context) => {
    const { STORAGE_ACCOUNT, STORAGE_KEY, RESUME_CONTAINER, RESUME_BLOB } = process.env;
    if (!STORAGE_ACCOUNT || !STORAGE_KEY || !RESUME_CONTAINER || !RESUME_BLOB) {
      return {
        status: 503,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ error: 'resume storage is not configured on this deployment' }),
      };
    }

    try {
      const sharedKey = new StorageSharedKeyCredential(STORAGE_ACCOUNT, STORAGE_KEY);
      const now = new Date();
      const expiry = new Date(now.getTime() + EXPIRY_MINUTES * 60 * 1000);

      const sas = generateBlobSASQueryParameters(
        {
          containerName: RESUME_CONTAINER,
          blobName: RESUME_BLOB,
          permissions: BlobSASPermissions.parse('r'),   // read-only
          protocol: SASProtocol.Https,                   // HTTPS only
          startsOn: new Date(now.getTime() - 60 * 1000), // 1 min clock-skew grace
          expiresOn: expiry,
          // force a clean download filename
          contentDisposition: `attachment; filename="${RESUME_BLOB}"`,
        },
        sharedKey,
      ).toString();

      const url =
        `https://${STORAGE_ACCOUNT}.blob.core.windows.net/` +
        `${RESUME_CONTAINER}/${encodeURIComponent(RESUME_BLOB)}?${sas}`;

      context.log(`resume SAS minted (expires ${expiry.toISOString()})`);
      return {
        status: 302,
        headers: {
          Location: url,
          'Cache-Control': 'no-store',
        },
      };
    } catch (err) {
      context.error('resume SAS mint failed:', err.message);
      return {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ error: 'could not generate resume link' }),
      };
    }
  },
});

// keep the SDK import referenced for tree-shaking clarity
void BlobServiceClient;
