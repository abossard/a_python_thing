// Generate random data points using Float32Array
function generateDataPoints(count, height) {
    const data = new Float32Array(count);
    for (let i = 0; i < count; i++) {
      data[i] = Math.random() * height;
    }
    return data;
  }
  
  // Handle messages from the main thread
  self.onmessage = (e) => {
    const { dataSize } = e.data;
    const height = 400; // Canvas height
    const dataPoints = generateDataPoints(dataSize, height);
    self.postMessage(dataPoints);
  };
  