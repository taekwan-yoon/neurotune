import React, { useState, useRef } from 'react';
import image1 from '../model/analysis.png';
import image2 from '../model/avgpsd.png';
import image3 from '../model/tfr_fig.png';
import './ImageSlider.css';

const ImageSliderModal = ({ closeModal }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [zoomLevel, setZoomLevel] = useState(1); // Initial zoom level
  const [isModalOpen, setIsModalOpen] = useState(true); // Modal open/close state
  const images = [image1, image2, image3];
  const imageRef = useRef(null); // Reference to the image for zooming

  // Function to go to the next image
  const nextImage = () => {
    setCurrentIndex((prevIndex) => (prevIndex + 1) % images.length);
  };

  // Function to go to the previous image
  const prevImage = () => {
    setCurrentIndex((prevIndex) => (prevIndex - 1 + images.length) % images.length);
  };

  // Function to handle zoom with mouse wheel
  const handleWheel = (event) => {
    event.preventDefault();
    
    const zoomFactor = 0.1;
    let newZoomLevel = zoomLevel + event.deltaY * -zoomFactor; // Adjust zoom speed here
    newZoomLevel = Math.min(Math.max(1, newZoomLevel), 3); // Limit zoom between 1 and 3
    setZoomLevel(newZoomLevel);

    // Calculate zoom on mouse position to make zooming feel more natural (center of the zoom is the mouse position)
    if (imageRef.current) {
      const rect = imageRef.current.getBoundingClientRect();
      const mouseX = event.clientX - rect.left; // Mouse X relative to the image
      const mouseY = event.clientY - rect.top; // Mouse Y relative to the image
      
      const zoomAdjustmentX = (mouseX / rect.width) * newZoomLevel * 0.2;
      const zoomAdjustmentY = (mouseY / rect.height) * newZoomLevel * 0.2;

      // Adjust the image's offset based on the mouse position during zoom
      imageRef.current.style.transformOrigin = `${(mouseX / rect.width) * 100}% ${(mouseY / rect.height) * 100}%`;
    }
  };

  const imageStyles = {
    transform: `scale(${zoomLevel})`, // Apply zoom
  };

  if (!isModalOpen) {
    return null; // Don't render anything if modal is closed
  }

  return (
    <div>
      <div className="modal-overlay" onWheel={handleWheel}>
        <div className="modal-content">
          <button className="close-btn" onClick={closeModal}>×</button>
          <div className="slider-container">
            <button className="prev-btn" onClick={prevImage}>←</button>
            <div className="slider">
              <img
                ref={imageRef}
                src={images[currentIndex]}
                alt={`Slide ${currentIndex + 1}`}
                className="slider-image"
                style={imageStyles}
              />
            </div>
            <button className="next-btn" onClick={nextImage}>→</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImageSliderModal;
