import React from 'react';
import styles from './styles.module.css';

const HardwareNotes = ({ gpuNotes, jetsonNotes }) => {
  const hasGpuNotes = gpuNotes && gpuNotes.trim().length > 0;
  const hasJetsonNotes = jetsonNotes && jetsonNotes.trim().length > 0;

  if (!hasGpuNotes && !hasJetsonNotes) {
    return (
      <div className={styles.hardwareNotesContainer}>
        <div className={styles.noteItem}>
          <div className={styles.noteHeader}>
            <span className={styles.noteIcon}>💻</span>
            <h3 className={styles.noteTitle}>Hardware Requirements</h3>
          </div>
          <div className={styles.noteContent}>
            <p>No specific hardware requirements noted for this section.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.hardwareNotesContainer}>
      {hasGpuNotes && (
        <div className={styles.noteItem}>
          <div className={styles.noteHeader}>
            <span className={styles.noteIcon}>🎮</span>
            <h3 className={styles.noteTitle}>GPU Workstation Notes</h3>
          </div>
          <div className={styles.noteContent}>
            <p>{gpuNotes}</p>
          </div>
        </div>
      )}

      {hasJetsonNotes && (
        <div className={styles.noteItem}>
          <div className={styles.noteHeader}>
            <span className={styles.noteIcon}>🤖</span>
            <h3 className={styles.noteTitle}>Jetson Edge Notes</h3>
          </div>
          <div className={styles.noteContent}>
            <p>{jetsonNotes}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default HardwareNotes;