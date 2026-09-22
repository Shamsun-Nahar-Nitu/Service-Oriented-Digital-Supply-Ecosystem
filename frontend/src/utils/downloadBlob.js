/** Saves a blob response to disk via a throwaway <a download> — the
 * standard way to turn an authenticated axios blob response into a file
 * save, since there's no <form> download target for an authenticated XHR
 * request. Shared by api/finance.js and api/payments.js so both PDF
 * downloads (dashboard reports, order receipts) work identically. */
export function triggerBlobDownload(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}