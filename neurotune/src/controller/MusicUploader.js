import React from "react";

const MusicUploader = ({ onFileUpload }) => {
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      onFileUpload(file);
    }
  };

  return (
    <div>
      <h2>Upload a Music File</h2>
      <input type="file" accept="audio/*" onChange={handleFileChange} />
    </div>
  );
};

export default MusicUploader;
