const express  = require('express');
const https    = require('https');
const socketIO = require('socket.io');
const fs       = require('fs');
const path     = require('path');
const cors     = require('cors');

const app    = express();
const server = https.createServer({
  key:  fs.readFileSync('key.pem'),
  cert: fs.readFileSync('cert.pem'),
}, app);
const io = socketIO(server, { maxHttpBufferSize: 1e8 });

const port = 3000;
let imageCount = 0;

// Serve index.html for all routes
app.use(cors());
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

io.on('connection', (socket) => {
  console.log('Phone connected');

  socket.on('takePicture', ({ imageData }) => {
    const base64Data  = imageData.replace(/^data:image\/jpeg;base64,/, '');
    const binaryData  = Buffer.from(base64Data, 'base64');
    const fileName    = `${imageCount}.jpg`;
    const filePath    = path.join(__dirname, 'public', fileName);

    fs.writeFileSync(filePath, binaryData);
    console.log(`Saved: ${fileName}`);
    imageCount++;

    // Acknowledge to phone so UI can update status
    socket.emit('pictureSaved', { fileName });
  });

  socket.on('disconnect', () => {
    console.log('Phone disconnected');
  });
});

server.listen(port, '0.0.0.0', () => {
  console.log(`Camera server running on https://0.0.0.0:${port}`);
  console.log(`Open on your phone: https://<your-pc-ip>:${port}`);
});
