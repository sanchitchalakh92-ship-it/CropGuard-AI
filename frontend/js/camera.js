/**
 * CropGuard AI - Camera & File Upload Management
 */

class CameraUploader {
  constructor(options = {}) {
    this.dropzone = options.dropzone;
    this.fileInput = options.fileInput;
    this.cameraInput = options.cameraInput;
    this.onImageSelected = options.onImageSelected || (() => {});

    this.initEvents();
  }

  initEvents() {
    if (this.dropzone) {
      // Drag and drop
      ['dragenter', 'dragover'].forEach(eventName => {
        this.dropzone.addEventListener(eventName, (e) => {
          e.preventDefault();
          this.dropzone.classList.add('dragover');
        }, false);
      });

      ['dragleave', 'drop'].forEach(eventName => {
        this.dropzone.addEventListener(eventName, (e) => {
          e.preventDefault();
          this.dropzone.classList.remove('dragover');
        }, false);
      });

      this.dropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files && files.length > 0) {
          this.handleFile(files[0]);
        }
      });
    }

    if (this.fileInput) {
      this.fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
          this.handleFile(e.target.files[0]);
        }
      });
    }

    if (this.cameraInput) {
      this.cameraInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
          this.handleFile(e.target.files[0]);
        }
      });
    }
  }

  async handleFile(file) {
    if (!file.type.startsWith('image/')) {
      alert("Please select a valid image file (JPEG, PNG, WebP).");
      return;
    }

    try {
      const { file: optimizedFile, dataUrl } = await this.optimizeImage(file);
      if (dataUrl) {
        this.onImageSelected({
          file: optimizedFile,
          dataUrl: dataUrl
        });
      }
    } catch (err) {
      console.warn("Client image optimization fallback:", err);
      const reader = new FileReader();
      reader.onload = (e) => {
        this.onImageSelected({
          file: file,
          dataUrl: e.target.result
        });
      };
      reader.readAsDataURL(file);
    }
  }

  async optimizeImage(file, maxDimension = 1280, quality = 0.85) {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          let width = img.width;
          let height = img.height;

          // If already appropriately sized and under 800KB, use directly
          if (width <= maxDimension && height <= maxDimension && file.size < 800 * 1024) {
            return resolve({ file, dataUrl: e.target.result });
          }

          if (width > height) {
            if (width > maxDimension) {
              height = Math.round((height * maxDimension) / width);
              width = maxDimension;
            }
          } else {
            if (height > maxDimension) {
              width = Math.round((width * maxDimension) / height);
              height = maxDimension;
            }
          }

          const canvas = document.createElement("canvas");
          canvas.width = width;
          canvas.height = height;
          const ctx = canvas.getContext("2d");
          ctx.drawImage(img, 0, 0, width, height);

          canvas.toBlob((blob) => {
            if (!blob) {
              return resolve({ file, dataUrl: e.target.result });
            }
            const cleanName = (file.name || "leaf.jpg").replace(/\.[^.]+$/, "") + ".jpg";
            const optimizedFile = new File([blob], cleanName, { type: "image/jpeg" });
            const optimizedDataUrl = canvas.toDataURL("image/jpeg", quality);
            resolve({ file: optimizedFile, dataUrl: optimizedDataUrl });
          }, "image/jpeg", quality);
        };
        img.onerror = () => resolve({ file, dataUrl: e.target.result });
        img.src = e.target.result;
      };
      reader.onerror = () => resolve({ file, dataUrl: null });
      reader.readAsDataURL(file);
    });
  }

  async loadSampleImageAsFile(imageUrl, filename) {
    const response = await fetch(imageUrl);
    const blob = await response.blob();
    const file = new File([blob], filename, { type: blob.type || "image/jpeg" });
    const reader = new FileReader();
    return new Promise((resolve) => {
      reader.onload = (e) => {
        resolve({
          file: file,
          dataUrl: e.target.result
        });
      };
      reader.readAsDataURL(file);
    });
  }
}
