import React, { useEffect, useRef } from 'react';
import styles from './styles.module.css';

const URDFVisualizer = ({ urdfPath, title = "URDF Model" }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    // In a real implementation, this would use a URDF visualization library
    // like react-three-urdf or similar to render the URDF model
    // For now, we'll create a placeholder visualization

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw a simple placeholder for the URDF visualization
    ctx.fillStyle = '#f0f0f0';
    ctx.fillRect(0, 0, width, height);

    // Draw a simple robot-like shape as a placeholder
    ctx.fillStyle = '#3498db';
    ctx.beginPath();
    ctx.arc(width / 2, height / 3, 30, 0, Math.PI * 2); // Head
    ctx.fill();

    ctx.fillStyle = '#2c3e50';
    ctx.fillRect(width / 2 - 15, height / 3 + 30, 30, 60); // Body

    ctx.fillRect(width / 2 - 50, height / 3 + 40, 35, 10); // Left arm
    ctx.fillRect(width / 2 + 15, height / 3 + 40, 35, 10); // Right arm

    ctx.fillRect(width / 2 - 20, height / 3 + 90, 15, 40); // Left leg
    ctx.fillRect(width / 2 + 5, height / 3 + 90, 15, 40); // Right leg

    // Add some details
    ctx.fillStyle = '#e74c3c';
    ctx.beginPath();
    ctx.arc(width / 2 - 10, height / 3 - 5, 5, 0, Math.PI * 2); // Left eye
    ctx.arc(width / 2 + 10, height / 3 - 5, 5, 0, Math.PI * 2); // Right eye
    ctx.fill();

    // Add text label
    ctx.fillStyle = '#2c3e50';
    ctx.font = '14px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(title, width / 2, height - 10);
  }, [urdfPath, title]);

  return (
    <div className={styles.urdfVisualizerContainer}>
      <h3 className={styles.visualizerTitle}>{title}</h3>
      <div className={styles.visualizerContent}>
        <canvas
          ref={canvasRef}
          width={400}
          height={300}
          className={styles.visualizerCanvas}
        />
        <div className={styles.controls}>
          <button className={styles.controlButton}>Rotate</button>
          <button className={styles.controlButton}>Zoom In</button>
          <button className={styles.controlButton}>Zoom Out</button>
        </div>
      </div>
      {urdfPath && (
        <div className={styles.urdfInfo}>
          <p>URDF File: {urdfPath}</p>
          <p className={styles.description}>This is a visualization of the robot model defined in the URDF file. In a real implementation, this would render the actual 3D model using a robotics visualization library.</p>
        </div>
      )}
    </div>
  );
};

export default URDFVisualizer;