const http = require("http");
const os = require("os");

const PORT = process.env.PORT || 3000;
const hostname = os.hostname();

const server = http.createServer((req, res) => {
  if (req.url === "/health/live" || req.url === "/health/ready") {
    res.writeHead(200, { "Content-Type": "text/plain" });
    return res.end("OK");
  }

  if (req.url === "/favicon.ico") {
    res.writeHead(204);
    return res.end();
  }

  if (req.url === "/") {
    res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });

    return res.end(`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Cloud Computing Lab</title>
  <style>
    * { box-sizing: border-box; }
    body {
      margin: 0; min-height: 100vh; display: grid; place-items: center;
      padding: 24px; font-family: Arial, sans-serif;
      background: linear-gradient(135deg, #101827, #183b56); color: #f8fafc;
    }
    main {
      width: min(680px, 100%); padding: 36px; border-radius: 20px;
      background: #ffffff12; border: 1px solid #ffffff25;
      box-shadow: 0 20px 60px #0004;
    }
    .tag { color: #7dd3fc; text-transform: uppercase; letter-spacing: 2px; font-size: 12px; }
    h1 { font-size: clamp(28px, 5vw, 42px); margin: 12px 0; }
    p { color: #dbeafe; line-height: 1.6; }
    .details { margin-top: 28px; display: grid; gap: 12px; }
    .item { padding: 16px; border-radius: 12px; background: #0003; overflow-wrap: anywhere; }
    .label { display: block; color: #bae6fd; font-size: 12px; margin-bottom: 7px; }
    .value { font-size: 17px; font-weight: bold; }
    footer { margin-top: 24px; font-size: 13px; color: #cbd5e1; }
  </style>
</head>
<body>
  <main>
    <div class="tag">Cloud Computing Lab · Assignment 4</div>
    <h1>Docker + Kubernetes</h1>
    <p>This web application is running inside a container managed by Kubernetes.</p>
    <div class="details">
      <div class="item"><span class="label">POD / CONTAINER HOSTNAME</span><span class="value">${hostname}</span></div>
      <div class="item"><span class="label">SERVER PORT</span><span class="value">${PORT}</span></div>
      <div class="item"><span class="label">SERVER TIME</span><span class="value">${new Date().toISOString()}</span></div>
    </div>
    <footer>Refresh the page to observe which replica serves your request. Repeated requests may reach different replicas.</footer>
  </main>
</body>
</html>`);
  }

  res.writeHead(404, { "Content-Type": "text/plain" });
  res.end("Not Found");
});

server.listen(PORT, "0.0.0.0", () => {
  console.log(`Web server running on port ${PORT}`);
  console.log(`Hostname: ${hostname}`);
});
