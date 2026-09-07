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

  handleFile(file) {
    if (!file.type.startsWith('image/')) {
      alert("Please select a valid image file (JPEG, PNG, WebP).");
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      this.onImageSelected({
        file: file,
        dataUrl: e.target.result
      });
    };
    reader.readAsDataURL(file);
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
