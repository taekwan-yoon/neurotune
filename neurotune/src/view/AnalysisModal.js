import React, { useState } from 'react';
import ImageSlider from './ImageSlider';  

const AnalysisModal = () => {

  // Function to open the
  return (
    <div>
      {/* Button to open the modal */}

      {/* Modal Overlay */}
      {
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>Image Slider</h2>
            <ImageSlider />  {/* Include the ImageSlider inside the modal */}
          </div>
        </div>
      }
    </div>
  );
};

export default AnalysisModal;
