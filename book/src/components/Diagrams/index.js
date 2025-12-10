import React from 'react';
import styles from './styles.module.css';

// Simple flowchart component
const Flowchart = ({ nodes, edges, title = "Flowchart" }) => {
  return (
    <div className={styles.diagramContainer}>
      <h3 className={styles.diagramTitle}>{title}</h3>
      <div className={styles.flowchart}>
        {nodes?.map((node, index) => (
          <div key={index} className={`${styles.node} ${styles[node.type || 'process']}`}>
            {node.label}
          </div>
        ))}
      </div>
    </div>
  );
};

// Simple architecture diagram component
const ArchitectureDiagram = ({ layers, connections, title = "Architecture" }) => {
  return (
    <div className={styles.diagramContainer}>
      <h3 className={styles.diagramTitle}>{title}</h3>
      <div className={styles.architecture}>
        {layers?.map((layer, index) => (
          <div key={index} className={styles.layer}>
            <h4 className={styles.layerTitle}>{layer.name}</h4>
            <div className={styles.layerComponents}>
              {layer.components?.map((comp, compIndex) => (
                <div key={compIndex} className={styles.component}>
                  {comp}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Simple UML class diagram component
const ClassDiagram = ({ classes, relationships, title = "Class Diagram" }) => {
  return (
    <div className={styles.diagramContainer}>
      <h3 className={styles.diagramTitle}>{title}</h3>
      <div className={styles.classDiagram}>
        {classes?.map((cls, index) => (
          <div key={index} className={styles.classBox}>
            <div className={styles.className}>{cls.name}</div>
            <div className={styles.classMethods}>
              {cls.methods?.map((method, methodIndex) => (
                <div key={methodIndex} className={styles.method}>
                  {method}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Main Diagrams component that can render different types
const Diagrams = ({ type, data, title }) => {
  switch (type) {
    case 'flowchart':
      return <Flowchart nodes={data.nodes} edges={data.edges} title={title} />;
    case 'architecture':
      return <ArchitectureDiagram layers={data.layers} connections={data.connections} title={title} />;
    case 'class':
      return <ClassDiagram classes={data.classes} relationships={data.relationships} title={title} />;
    default:
      return (
        <div className={styles.diagramContainer}>
          <h3 className={styles.diagramTitle}>{title || 'Diagram'}</h3>
          <div className={styles.defaultDiagram}>
            <p>Diagram type "{type}" not recognized.</p>
          </div>
        </div>
      );
  }
};

export default Diagrams;
export { Flowchart, ArchitectureDiagram, ClassDiagram };