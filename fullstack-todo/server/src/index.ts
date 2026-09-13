import { DATA_FILE, PORT } from './config.js';
import { createApp } from './app.js';

const app = createApp();

app.listen(PORT, () => {
  console.log(`API      -> http://localhost:${PORT}/api/health`);
  console.log(`Data file -> ${DATA_FILE}`);
});
