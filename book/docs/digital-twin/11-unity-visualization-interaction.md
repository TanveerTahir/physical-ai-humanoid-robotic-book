---
title: Unity Visualization & Interaction
sidebar_position: 3
description: Using Unity for advanced visualization and interaction in digital twin environments
gpu_notes: This chapter requires Unity with HDRP; minimum 8GB VRAM recommended for advanced rendering
jetson_notes: Unity simulation not supported on Jetson; use for visualization only on GPU workstation
---

# Unity Visualization & Interaction

## Prerequisites

Before studying this chapter, you should have:
- Understanding of basic 3D graphics concepts and game engines
- Experience with physics simulation concepts (from Chapter 10)
- Basic knowledge of humanoid robot kinematics and dynamics
- Familiarity with ROS2 integration concepts (from Chapter 5)
- Understanding of digital twin concepts (from Chapter 9)

## Learning Objectives

By the end of this chapter, you should be able to:
- Set up Unity for humanoid robot visualization and simulation
- Implement realistic physics and collision systems for humanoid robots
- Create interactive environments for robot testing and training
- Integrate Unity with ROS2 for bidirectional communication
- Develop advanced visualization techniques for robot data
- Optimize Unity scenes for real-time performance with complex humanoid models

## Introduction

Unity has emerged as a powerful platform for creating advanced digital twin environments, particularly for humanoid robotics applications. Unlike traditional simulation environments like Gazebo, Unity offers advanced rendering capabilities, intuitive visual scripting, and a rich ecosystem of assets and tools. This makes it ideal for creating photorealistic environments and complex interaction scenarios for humanoid robots.

Unity's strength lies in its ability to create visually compelling environments that closely resemble real-world settings, which is crucial for sim-to-real transfer learning. Combined with its robust physics engine and extensive asset store, Unity provides a comprehensive platform for developing sophisticated digital twin environments for humanoid robots.

## Unity Setup for Robotics

### Installing Unity Hub and Unity Editor

For robotics applications, we recommend Unity 2022.3 LTS (Long Term Support) with the following packages:

1. **Unity Editor** with Universal Render Pipeline (URP) or High Definition Render Pipeline (HDRP)
2. **Visual Studio Tools for Unity** for C# development
3. **Unity Recorder** for capturing simulation footage
4. **Timeline** for creating cinematic sequences

### Required Packages for Robotics

```json
{
  "dependencies": {
    "com.unity.robotics.ros-tcp-connector": "0.7.0",
    "com.unity.robotics.urdf-importer": "0.5.2",
    "com.unity.inputsystem": "1.7.0",
    "com.unity.timeline": "1.8.6",
    "com.unity.visualeffectgraph": "12.1.12",
    "com.unity.probuilder": "5.2.2"
  }
}
```

### Project Structure for Robotics

```
Unity Humanoid Robotics Project/
├── Assets/
│   ├── Scripts/           # C# scripts for robot control and simulation
│   │   ├── ROS/          # ROS communication scripts
│   │   ├── Robotics/     # Robot-specific scripts
│   │   └── Simulation/   # Simulation control scripts
│   ├── Models/           # 3D models for robots and environments
│   │   ├── Robots/       # Humanoid robot models
│   │   ├── Environments/ # Scene environments
│   │   └── Props/        # Environmental props
│   ├── Materials/        # Material definitions
│   ├── Scenes/           # Unity scene files
│   ├── Prefabs/          # Reusable robot and environment prefabs
│   ├── Animations/       # Animation files
│   └── Resources/        # Runtime-loadable resources
├── Packages/             # Unity package definitions
├── ProjectSettings/      # Project configuration
└── Logs/                 # Simulation logs
```

## Creating Humanoid Robot Models in Unity

### Importing URDF Models

Unity's URDF Importer allows importing robot models from ROS/URDF format:

```csharp
using UnityEngine;
using Unity.Robotics.URDFImporter;

public class HumanoidRobotLoader : MonoBehaviour
{
    [SerializeField] private string robotUrdfPath = "Assets/Models/Robots/";
    [SerializeField] private string robotName = "humanoid_robot";

    void Start()
    {
        LoadRobotFromURDF();
    }

    private void LoadRobotFromURDF()
    {
        // Load URDF robot
        GameObject robot = URDFAssetPathUtils.LoadURDF(
            robotUrdfPath + robotName + "/urdf/" + robotName + ".urdf"
        );

        if (robot != null)
        {
            // Position the robot in the scene
            robot.transform.SetParent(transform);
            robot.transform.localPosition = Vector3.zero;
            robot.transform.localRotation = Quaternion.identity;

            // Configure physics for humanoid
            ConfigureRobotPhysics(robot);

            Debug.Log($"Successfully loaded robot: {robotName}");
        }
        else
        {
            Debug.LogError($"Failed to load robot from URDF: {robotUrdfPath}");
        }
    }

    private void ConfigureRobotPhysics(GameObject robot)
    {
        // Add Rigidbody components to links
        var links = robot.GetComponentsInChildren<Transform>();

        foreach (Transform link in links)
        {
            // Skip if already has Rigidbody
            if (link.GetComponent<Rigidbody>() != null)
                continue;

            // Add Rigidbody if it's a physical link
            if (IsPhysicalLink(link.name))
            {
                var rb = link.gameObject.AddComponent<Rigidbody>();

                // Configure for humanoid physics
                rb.mass = GetLinkMass(link.name);
                rb.drag = 0.1f;
                rb.angularDrag = 0.1f;
                rb.useGravity = true;
                rb.interpolation = RigidbodyInterpolation.Interpolate;

                // Add collider
                AddAppropriateCollider(link.gameObject);
            }
        }
    }

    private bool IsPhysicalLink(string linkName)
    {
        // Define which links should have physics
        string[] physicalLinks = {
            "torso", "head", "left_arm", "right_arm",
            "left_leg", "right_leg", "left_foot", "right_foot"
        };

        foreach (string physicalLink in physicalLinks)
        {
            if (linkName.ToLower().Contains(physicalLink))
                return true;
        }

        return false;
    }

    private float GetLinkMass(string linkName)
    {
        // Define mass based on link type
        if (linkName.Contains("torso")) return 10.0f;
        if (linkName.Contains("head")) return 2.0f;
        if (linkName.Contains("arm")) return 1.5f;
        if (linkName.Contains("leg")) return 5.0f;
        if (linkName.Contains("foot")) return 1.0f;

        return 0.5f; // Default mass
    }

    private void AddAppropriateCollider(GameObject link)
    {
        // Add appropriate collider based on link geometry
        // This would typically analyze the mesh or use URDF geometry info

        // For now, use a simple sphere collider as example
        var sphereCollider = link.AddComponent<SphereCollider>();
        sphereCollider.radius = 0.1f; // Adjust based on actual link size
    }
}
```

### Setting Up Articulation Bodies for Physics

For more advanced physics simulation, Unity's ArticulationBody component provides better performance than traditional joints:

```csharp
using UnityEngine;
using System.Collections.Generic;

public class HumanoidArticulationSetup : MonoBehaviour
{
    [System.Serializable]
    public class JointDefinition
    {
        public string jointName;
        public ArticulationJointType jointType;
        public Vector3 axis = Vector3.right;
        public float lowerLimit = -45f;
        public float upperLimit = 45f;
        public float stiffness = 1000f;
        public float damping = 100f;
    }

    [SerializeField] private List<JointDefinition> jointDefinitions = new List<JointDefinition>();
    [SerializeField] private float driveForceLimit = 1000f;

    void Start()
    {
        SetupArticulationChain();
    }

    private void SetupArticulationChain()
    {
        // Get all links in the robot hierarchy
        var links = GetComponentsInChildren<Transform>();

        foreach (Transform link in links)
        {
            var articulationBody = link.GetComponent<ArticulationBody>();
            if (articulationBody == null)
            {
                articulationBody = link.gameObject.AddComponent<ArticulationBody>();
            }

            // Configure the articulation body
            ConfigureArticulationBody(articulationBody, link.name);
        }

        // Set up joints between parent-child pairs
        foreach (Transform link in links)
        {
            if (link.parent != null && link.parent.GetComponent<ArticulationBody>() != null)
            {
                SetupJoint(link.parent.GetComponent<ArticulationBody>(),
                          link.GetComponent<ArticulationBody>());
            }
        }
    }

    private void ConfigureArticulationBody(ArticulationBody body, string linkName)
    {
        body.mass = GetLinkMass(linkName);
        body.linearDamping = 0.05f;
        body.angularDamping = 0.1f;
        body.jointFriction = 0.05f;
        body.enableGravity = true;
        body.sleepThreshold = 0.005f;
    }

    private void SetupJoint(ArticulationBody parent, ArticulationBody child)
    {
        // Configure joint properties
        var jointDrive = new ArticulationDrive();
        jointDrive.forceLimit = driveForceLimit;
        jointDrive.damping = 100f;
        jointDrive.stiffness = 1000f;

        child.jointAnchor = Vector3.zero; // Joint at center of child
        child.jointType = ArticulationJointType.RevoluteJoint;
        child.linearLockX = ArticulationDofLock.Locked;
        child.linearLockY = ArticulationDofLock.Locked;
        child.linearLockZ = ArticulationDofLock.Locked;

        // Set angular limits if needed
        var swingLimit = new ArticulationLimit();
        swingLimit.upper = 90f;
        swingLimit.lower = -90f;
        child.swingYLimit = swingLimit;
        child.twistLimit = swingLimit;
    }

    private float GetLinkMass(string linkName)
    {
        // Same implementation as in previous example
        if (linkName.Contains("torso")) return 10.0f;
        if (linkName.Contains("head")) return 2.0f;
        if (linkName.Contains("arm")) return 1.5f;
        if (linkName.Contains("leg")) return 5.0f;
        if (linkName.Contains("foot")) return 1.0f;

        return 0.5f;
    }
}
```

## Physics Configuration for Humanoid Robots

### Advanced Physics Settings

For realistic humanoid physics simulation in Unity:

```csharp
using UnityEngine;

[CreateAssetMenu(fileName = "HumanoidPhysicsConfig", menuName = "Robotics/Humanoid Physics Config")]
public class HumanoidPhysicsConfig : ScriptableObject
{
    [Header("General Physics Settings")]
    public float gravityScale = 1.0f;
    public float simulationStep = 0.02f; // 50 FPS physics

    [Header("Balance and Stability")]
    public float balanceStiffness = 1500f;
    public float balanceDamping = 200f;
    public float balanceForceLimit = 500f;

    [Header("Walking Parameters")]
    public float stepHeight = 0.1f;
    public float stepLength = 0.3f;
    public float walkingSpeed = 0.5f;
    public float maxWalkingSpeed = 1.5f;

    [Header("Contact Sensing")]
    public float contactThreshold = 0.01f;
    public float contactPersistence = 0.1f;

    [Header("Joint Constraints")]
    public float jointStiffness = 1000f;
    public float jointDamping = 100f;
    public float jointForceLimit = 1000f;

    [Header("Foot Contact")]
    public float footContactRadius = 0.05f;
    public float footFriction = 0.8f;
    public float footRestitution = 0.1f;

    [Header("COM Control")]
    public float comHeight = 0.8f; // Center of mass height
    public float comStabilityRadius = 0.1f; // Acceptable COM deviation
    public float comCorrectionStrength = 50f;
}

public class PhysicsController : MonoBehaviour
{
    [SerializeField] private HumanoidPhysicsConfig config;

    private void Start()
    {
        ConfigurePhysicsEngine();
    }

    private void ConfigurePhysicsEngine()
    {
        // Set global physics parameters
        Physics.gravity = new Vector3(0, -9.81f * config.gravityScale, 0);

        // Set physics timestep
        Time.fixedDeltaTime = config.simulationStep;

        // Configure default physics material
        Physics.defaultMaterial = CreateDefaultPhysicsMaterial();
    }

    private PhysicMaterial CreateDefaultPhysicsMaterial()
    {
        PhysicMaterial material = new PhysicMaterial("HumanoidDefault");
        material.staticFriction = config.footFriction;
        material.dynamicFriction = config.footFriction;
        material.bounciness = config.footRestitution;
        material.frictionCombine = PhysicMaterialCombine.Maximum;
        material.bounceCombine = PhysicMaterialCombine.Average;

        return material;
    }
}
```

### Collision Detection Optimization

For humanoid robots with many links, optimizing collision detection is crucial:

```csharp
using UnityEngine;
using System.Collections.Generic;

public class CollisionOptimizer : MonoBehaviour
{
    [SerializeField] private float contactCheckInterval = 0.1f;
    [SerializeField] private LayerMask collisionLayers = -1;

    private Dictionary<string, Collider[]> linkColliders = new Dictionary<string, Collider[]>();
    private Dictionary<string, bool> contactStates = new Dictionary<string, bool>();

    private float lastContactCheckTime = 0f;

    void Start()
    {
        SetupCollisionDetection();
    }

    void FixedUpdate()
    {
        if (Time.time - lastContactCheckTime >= contactCheckInterval)
        {
            CheckContacts();
            lastContactCheckTime = Time.time;
        }
    }

    private void SetupCollisionDetection()
    {
        var links = GetComponentsInChildren<Transform>();

        foreach (Transform link in links)
        {
            var colliders = link.GetComponents<Collider>();
            if (colliders.Length > 0)
            {
                linkColliders[link.name] = colliders;
                contactStates[link.name] = false;
            }
        }
    }

    private void CheckContacts()
    {
        foreach (var kvp in linkColliders)
        {
            string linkName = kvp.Key;
            Collider[] colliders = kvp.Value;

            bool isTouching = false;

            foreach (Collider col in colliders)
            {
                // Use overlap sphere to detect nearby objects efficiently
                Collider[] nearbyObjects = Physics.OverlapSphere(
                    col.bounds.center,
                    col.bounds.extents.magnitude + 0.05f,  // Slightly larger than bounds
                    collisionLayers
                );

                foreach (Collider nearbyCol in nearbyObjects)
                {
                    if (nearbyCol != col && !nearbyCol.isTrigger)
                    {
                        // Check actual contact by testing bounds overlap
                        if (col.bounds.Intersects(nearbyCol.bounds))
                        {
                            isTouching = true;

                            // Trigger contact event
                            OnContactDetected(linkName, nearbyCol.gameObject.name);
                            break;
                        }
                    }
                }
            }

            // Update contact state
            bool previousState = contactStates[linkName];
            contactStates[linkName] = isTouching;

            // Trigger contact state change events
            if (previousState != isTouching)
            {
                if (isTouching)
                {
                    OnContactStarted(linkName);
                }
                else
                {
                    OnContactEnded(linkName);
                }
            }
        }
    }

    private void OnContactDetected(string linkName, string otherObjectName)
    {
        // Handle contact detection
        if (linkName.Contains("foot"))
        {
            // Foot contact - important for walking gait
            SendMessage("OnFootContact", linkName, SendMessageOptions.DontRequireReceiver);
        }
        else if (linkName.Contains("hand"))
        {
            // Hand contact - important for manipulation
            SendMessage("OnHandContact", linkName, SendMessageOptions.DontRequireReceiver);
        }
    }

    private void OnContactStarted(string linkName)
    {
        // Handle when contact starts
        Debug.Log($"Contact started: {linkName}");
    }

    private void OnContactEnded(string linkName)
    {
        // Handle when contact ends
        Debug.Log($"Contact ended: {linkName}");
    }
}
```

## Advanced Visualization Techniques

### Real-time Sensor Visualization

Visualizing sensor data in real-time enhances the debugging and understanding of robot behavior:

```csharp
using UnityEngine;
using System.Collections.Generic;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Sensor;

public class SensorVisualizer : MonoBehaviour
{
    [SerializeField] private LineRenderer laserScanRenderer;
    [SerializeField] private GameObject cameraVisualization;
    [SerializeField] private Color sensorColor = Color.yellow;
    [SerializeField] private float visualizationDuration = 0.1f;

    private List<Vector3> laserPoints = new List<Vector3>();
    private ROSConnection ros;

    void Start()
    {
        ros = ROSConnection.instance;

        // Subscribe to sensor topics
        ros.Subscribe<LaserScanMsg>("/scan", OnLaserScanReceived);
        ros.Subscribe<ImageMsg>("/camera/image_raw", OnCameraImageReceived);

        SetupVisualizers();
    }

    private void SetupVisualizers()
    {
        // Setup laser scan visualization
        if (laserScanRenderer != null)
        {
            laserScanRenderer.material = new Material(Shader.Find("Sprites/Default"));
            laserScanRenderer.startWidth = 0.02f;
            laserScanRenderer.endWidth = 0.02f;
            laserScanRenderer.startColor = sensorColor;
            laserScanRenderer.endColor = sensorColor;
            laserScanRenderer.enabled = true;
        }
    }

    private void OnLaserScanReceived(LaserScanMsg scanMsg)
    {
        // Convert laser scan to Unity coordinates
        laserPoints.Clear();

        Vector3 robotPosition = transform.position;
        Quaternion robotRotation = transform.rotation;

        for (int i = 0; i < scanMsg.ranges.Count; i++)
        {
            float angle = scanMsg.angle_min + (i * scanMsg.angle_increment);
            float distance = (float)scanMsg.ranges[i];

            if (distance >= scanMsg.range_min && distance <= scanMsg.range_max)
            {
                // Calculate point in laser frame
                Vector3 pointInLaserFrame = new Vector3(
                    distance * Mathf.Cos(angle),
                    0,  // Assuming 2D scan
                    distance * Mathf.Sin(angle)
                );

                // Transform to world coordinates
                Vector3 worldPoint = robotRotation * pointInLaserFrame + robotPosition;
                laserPoints.Add(worldPoint);
            }
        }

        // Update line renderer
        if (laserScanRenderer != null && laserPoints.Count > 1)
        {
            laserScanRenderer.positionCount = laserPoints.Count;
            laserScanRenderer.SetPositions(laserPoints.ToArray());
        }
    }

    private void OnCameraImageReceived(ImageMsg imageMsg)
    {
        // For camera visualization, we could texture a quad or apply to material
        // This is a simplified approach - in practice, you'd convert the image format
        StartCoroutine(UpdateCameraTexture(imageMsg));
    }

    private System.Collections.IEnumerator UpdateCameraTexture(ImageMsg imageMsg)
    {
        // Convert ROS image to Unity texture (simplified)
        // In practice, you'd need to handle the specific encoding format

        Texture2D texture = new Texture2D((int)imageMsg.width, (int)imageMsg.height);

        // Process image data based on encoding
        if (imageMsg.encoding == "rgb8" || imageMsg.encoding == "bgr8")
        {
            // Process RGB/BGR data
            Color32[] colors = new Color32[imageMsg.data.Count / 3];

            for (int i = 0; i < colors.Length; i++)
            {
                int idx = i * 3;
                if (idx + 2 < imageMsg.data.Count)
                {
                    byte r = imageMsg.data[idx];
                    byte g = imageMsg.data[idx + 1];
                    byte b = imageMsg.data[idx + 2];

                    // For BGR, swap R and B
                    if (imageMsg.encoding == "bgr8")
                    {
                        colors[i] = new Color32(b, g, r, 255);
                    }
                    else
                    {
                        colors[i] = new Color32(r, g, b, 255);
                    }
                }
            }

            texture.SetPixels32(colors);
            texture.Apply();

            // Apply to material
            if (cameraVisualization != null)
            {
                Renderer rend = cameraVisualization.GetComponent<Renderer>();
                if (rend != null && rend.materials.Length > 0)
                {
                    rend.material.mainTexture = texture;
                }
            }
        }

        yield return new WaitForSeconds(visualizationDuration);
    }

    // Method to visualize IMU data
    public void VisualizeIMU(Vector3 orientation, Vector3 angularVelocity, Vector3 linearAcceleration)
    {
        // Create visual indicators for IMU data
        // Orientation: show orientation with colored arrows
        // Angular velocity: show with rotating indicators
        // Acceleration: show with directional arrows

        // Example: Visualize orientation as a coordinate frame
        GameObject orientationIndicator = new GameObject("OrientationIndicator");
        orientationIndicator.transform.SetParent(transform);
        orientationIndicator.transform.localPosition = Vector3.zero;

        // Create X, Y, Z axes indicators
        CreateAxisIndicator(orientationIndicator.transform, Vector3.right, Color.red, "X");
        CreateAxisIndicator(orientationIndicator.transform, Vector3.up, Color.green, "Y");
        CreateAxisIndicator(orientationIndicator.transform, Vector3.forward, Color.blue, "Z");

        // Destroy after visualization duration
        Destroy(orientationIndicator, visualizationDuration);
    }

    private void CreateAxisIndicator(Transform parent, Vector3 direction, Color color, string name)
    {
        GameObject axis = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        axis.name = name + "_Axis";
        axis.transform.SetParent(parent);
        axis.transform.localScale = new Vector3(0.02f, 0.2f, 0.02f);  // Make thin cylinder

        // Orient to point in the right direction
        axis.transform.rotation = Quaternion.FromToRotation(Vector3.up, direction);
        axis.transform.position = parent.position + direction * 0.1f;  // Offset slightly

        // Change color
        Renderer rend = axis.GetComponent<Renderer>();
        if (rend != null)
        {
            rend.material.color = color;
        }

        // Remove collider for performance
        DestroyImmediate(axis.GetComponent<Collider>());
    }
}
```

### Animation and Movement Visualization

Creating realistic humanoid movement visualization:

```csharp
using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class HumanoidAnimationController : MonoBehaviour
{
    [Header("Walking Parameters")]
    [SerializeField] private float walkCycleDuration = 1.0f;
    [SerializeField] private float walkSpeedMultiplier = 1.0f;
    [SerializeField] private float stepHeight = 0.1f;
    [SerializeField] private float leanAmount = 0.05f;

    [Header("IK Settings")]
    [SerializeField] private bool useFootIK = true;
    [SerializeField] private bool useHandIK = true;
    [SerializeField] private LayerMask groundLayer = 1;

    [Header("Visualization")]
    [SerializeField] private GameObject centerOfMassIndicator;
    [SerializeField] private GameObject zeroMomentPointIndicator;

    private Animator animator;
    private float walkCycleTime = 0f;
    private Vector3 targetVelocity = Vector3.zero;
    private Vector3 currentVelocity = Vector3.zero;
    private Vector3 comPosition = Vector3.zero;

    void Start()
    {
        animator = GetComponent<Animator>();
        if (animator == null)
        {
            animator = gameObject.AddComponent<Animator>();
        }

        SetupIndicators();
    }

    void Update()
    {
        UpdateWalkingAnimation();
        UpdateCenterOfMass();
        UpdateZeroMomentPoint();
    }

    private void UpdateWalkingAnimation()
    {
        // Update walk cycle time
        walkCycleTime += Time.deltaTime;
        if (walkCycleTime > walkCycleDuration)
            walkCycleTime = 0f;

        // Calculate walk parameters
        float walkPhase = walkCycleTime / walkCycleDuration;
        float leftFootPhase = (walkPhase + 0.5f) % 1.0f;  // Offset by half cycle
        float rightFootPhase = walkPhase;

        // Apply foot lifting animation
        if (useFootIK)
        {
            ApplyFootIK("LeftFoot", leftFootPhase);
            ApplyFootIK("RightFoot", rightFootPhase);
        }

        // Apply body lean for balance
        ApplyBodyLean(walkPhase);

        // Update animator parameters
        if (animator != null)
        {
            animator.SetFloat("WalkSpeed", targetVelocity.magnitude * walkSpeedMultiplier);
            animator.SetFloat("WalkPhase", walkPhase);
        }
    }

    private void ApplyFootIK(string footName, float phase)
    {
        Transform footTransform = FindChildRecursive(transform, footName);
        if (footTransform != null)
        {
            // Calculate lift based on phase (sinusoidal for smooth motion)
            float liftAmount = Mathf.Sin(phase * Mathf.PI * 2) * stepHeight;

            // Only lift during upward phase (first half of cycle)
            if (phase < 0.5f)
            {
                liftAmount = Mathf.Sin(phase * Mathf.PI) * stepHeight;
            }
            else
            {
                // During downward phase, check for ground contact
                RaycastHit hit;
                Vector3 rayStart = footTransform.position + Vector3.up * 0.1f;
                if (Physics.Raycast(rayStart, Vector3.down, out hit, 0.2f, groundLayer))
                {
                    // Foot should be at ground level
                    Vector3 newPosition = footTransform.position;
                    newPosition.y = hit.point.y + footTransform.lossyOffset.y;
                    footTransform.position = newPosition;
                    return;
                }
                else
                {
                    // Smoothly transition down
                    liftAmount = Mathf.Sin(Mathf.PI + (phase - 0.5f) * Mathf.PI) * stepHeight;
                }
            }

            // Apply lift
            Vector3 newPosition = footTransform.position;
            newPosition.y += liftAmount;
            footTransform.position = newPosition;
        }
    }

    private void ApplyBodyLean(float phase)
    {
        // Apply subtle body lean to counteract foot movement
        float leanDirection = Mathf.Sin(phase * Mathf.PI * 2);
        float leanAngle = leanAmount * leanDirection * 10f; // Convert to degrees

        // Apply to spine/torso
        Transform spine = FindChildRecursive(transform, "Spine") ??
                         FindChildRecursive(transform, "torso") ??
                         transform;  // Fallback to root

        if (spine != null)
        {
            Vector3 eulerAngles = spine.eulerAngles;
            eulerAngles.z = leanAngle;  // Lean side to side
            spine.eulerAngles = eulerAngles;
        }
    }

    private void UpdateCenterOfMass()
    {
        // Calculate approximate center of mass
        Vector3 totalWeightedPos = Vector3.zero;
        float totalMass = 0f;

        var links = GetComponentsInChildren<Transform>();
        foreach (Transform link in links)
        {
            Rigidbody rb = link.GetComponent<Rigidbody>();
            if (rb != null)
            {
                totalWeightedPos += link.position * rb.mass;
                totalMass += rb.mass;
            }
        }

        if (totalMass > 0)
        {
            comPosition = totalWeightedPos / totalMass;

            // Update COM indicator if it exists
            if (centerOfMassIndicator != null)
            {
                centerOfMassIndicator.transform.position = comPosition;
            }
        }
    }

    private void UpdateZeroMomentPoint()
    {
        // Simplified ZMP calculation
        // In reality, this would require more complex physics calculations
        Vector3 zmp = comPosition;
        zmp.y = transform.position.y;  // Project to ground level

        // For now, just visualize COM projected to ground
        if (zeroMomentPointIndicator != null)
        {
            zeroMomentPointIndicator.transform.position = zmp;
        }
    }

    private Transform FindChildRecursive(Transform parent, string name)
    {
        if (parent.name == name)
            return parent;

        for (int i = 0; i < parent.childCount; i++)
        {
            Transform result = FindChildRecursive(parent.GetChild(i), name);
            if (result != null)
                return result;
        }

        return null;
    }

    private void SetupIndicators()
    {
        if (centerOfMassIndicator == null)
        {
            centerOfMassIndicator = CreateIndicatorSphere("CenterOfMass", Color.red);
        }

        if (zeroMomentPointIndicator == null)
        {
            zeroMomentPointIndicator = CreateIndicatorSphere("ZeroMomentPoint", Color.blue);
        }

        // Initially hide indicators
        if (centerOfMassIndicator != null) centerOfMassIndicator.SetActive(false);
        if (zeroMomentPointIndicator != null) zeroMomentPointIndicator.SetActive(false);
    }

    private GameObject CreateIndicatorSphere(string name, Color color)
    {
        GameObject indicator = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        indicator.name = name;
        indicator.transform.SetParent(transform);
        indicator.transform.localScale = Vector3.one * 0.05f;  // Small sphere

        Renderer rend = indicator.GetComponent<Renderer>();
        if (rend != null)
        {
            rend.material = new Material(Shader.Find("Sprites/Default"));
            rend.material.color = color;
        }

        // Remove collider
        DestroyImmediate(indicator.GetComponent<Collider>());

        return indicator;
    }

    // Public methods to control animation
    public void SetTargetVelocity(Vector3 velocity)
    {
        targetVelocity = velocity;
    }

    public void EnableCOMVisualization(bool enable)
    {
        if (centerOfMassIndicator != null)
            centerOfMassIndicator.SetActive(enable);
    }

    public void EnableZMPVisualization(bool enable)
    {
        if (zeroMomentPointIndicator != null)
            zeroMomentPointIndicator.SetActive(enable);
    }
}
```

## ROS2 Integration with Unity

### Setting up ROS-TCP-Connector

The ROS-TCP-Connector enables communication between Unity and ROS2:

```csharp
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Std;
using RosMessageTypes.Geometry;
using RosMessageTypes.Sensor;

public class UnityROSBridge : MonoBehaviour
{
    [Header("ROS Connection")]
    [SerializeField] private string rosIPAddress = "127.0.0.1";
    [SerializeField] private int rosPort = 10000;

    [Header("Topic Names")]
    [SerializeField] private string jointStateTopic = "/joint_states";
    [SerializeField] private string cmdVelTopic = "/cmd_vel";
    [SerializeField] private string odomTopic = "/odom";

    private ROSConnection ros;
    private float publishRate = 0.05f; // 20 Hz
    private float lastPublishTime = 0f;

    // Robot joint states
    private string[] jointNames;
    private float[] jointPositions;
    private float[] jointVelocities;
    private float[] jointEfforts;

    void Start()
    {
        // Initialize ROS connection
        ros = ROSConnection.instance;
        ros.Initialize(rosIPAddress, rosPort);

        // Set up publishers and subscribers
        SetupROSCommunication();

        // Initialize joint arrays
        InitializeJointArrays();

        Debug.Log($"ROS Bridge initialized. Connecting to {rosIPAddress}:{rosPort}");
    }

    void Update()
    {
        if (Time.time - lastPublishTime >= publishRate)
        {
            PublishJointStates();
            lastPublishTime = Time.time;
        }
    }

    private void SetupROSCommunication()
    {
        // Subscribe to command topics
        ros.Subscribe<TwistMsg>(cmdVelTopic, OnCmdVelReceived);

        // Publishers are set up when needed
    }

    private void InitializeJointArrays()
    {
        // This would typically come from the robot model
        // For now, use a simple humanoid model
        jointNames = new string[] {
            "left_hip_pitch", "left_knee", "left_ankle",
            "right_hip_pitch", "right_knee", "right_ankle",
            "left_shoulder", "left_elbow",
            "right_shoulder", "right_elbow"
        };

        jointPositions = new float[jointNames.Length];
        jointVelocities = new float[jointNames.Length];
        jointEfforts = new float[jointNames.Length];

        // Initialize with neutral positions
        for (int i = 0; i < jointPositions.Length; i++)
        {
            jointPositions[i] = 0f;
            jointVelocities[i] = 0f;
            jointEfforts[i] = 0f;
        }
    }

    private void OnCmdVelReceived(TwistMsg cmdVel)
    {
        // Process velocity command
        Vector3 linear = new Vector3((float)cmdVel.linear.x, (float)cmdVel.linear.y, (float)cmdVel.linear.z);
        Vector3 angular = new Vector3((float)cmdVel.angular.x, (float)cmdVel.angular.y, (float)cmdVel.angular.z);

        // Apply to robot (this would depend on your robot's locomotion system)
        ApplyVelocityCommand(linear, angular);
    }

    private void ApplyVelocityCommand(Vector3 linear, Vector3 angular)
    {
        // This is where you'd implement the actual robot control logic
        // For a humanoid, this might involve:
        // - Converting to walking gait parameters
        // - Applying inverse kinematics
        // - Sending joint commands

        Debug.Log($"Received velocity command: linear={linear}, angular={angular}");
    }

    private void PublishJointStates()
    {
        // Update joint positions from Unity articulation bodies or other control system
        UpdateJointPositions();

        // Create and publish joint state message
        JointStateMsg jointStateMsg = new JointStateMsg();
        jointStateMsg.name = jointNames;

        // Convert float arrays to double arrays for ROS
        jointStateMsg.position = new double[jointPositions.Length];
        jointStateMsg.velocity = new double[jointVelocities.Length];
        jointStateMsg.effort = new double[jointEfforts.Length];

        for (int i = 0; i < jointPositions.Length; i++)
        {
            jointStateMsg.position[i] = jointPositions[i];
            jointStateMsg.velocity[i] = jointVelocities[i];
            jointStateMsg.effort[i] = jointEfforts[i];
        }

        jointStateMsg.header = new std_msgs.HeaderMsg();
        jointStateMsg.header.stamp = new builtin_interfaces.TimeMsg();
        jointStateMsg.header.frame_id = "base_link";

        ros.Publish(jointStateTopic, jointStateMsg);
    }

    private void UpdateJointPositions()
    {
        // Update joint positions from the actual Unity robot model
        // This would involve reading from ArticulationBodies or other Unity components

        // For now, simulate some movement
        float time = Time.time;
        for (int i = 0; i < jointPositions.Length; i++)
        {
            // Oscillate each joint differently
            jointPositions[i] = Mathf.Sin(time + i) * 0.2f;
            jointVelocities[i] = Mathf.Cos(time + i) * 0.2f;
        }
    }

    // Method to publish odometry
    public void PublishOdometry(Vector3 position, Quaternion rotation, Vector3 linearVelocity, Vector3 angularVelocity)
    {
        OdometryMsg odomMsg = new OdometryMsg();
        odomMsg.header = new std_msgs.HeaderMsg();
        odomMsg.header.stamp = new builtin_interfaces.TimeMsg();
        odomMsg.header.frame_id = "odom";
        odomMsg.child_frame_id = "base_link";

        // Position
        odomMsg.pose.pose.position = new geometry_msgs.PointMsg(position.x, position.y, position.z);
        odomMsg.pose.pose.orientation = new geometry_msgs.QuaternionMsg(rotation.x, rotation.y, rotation.z, rotation.w);

        // Velocity
        odomMsg.twist.twist.linear = new geometry_msgs.Vector3Msg(linearVelocity.x, linearVelocity.y, linearVelocity.z);
        odomMsg.twist.twist.angular = new geometry_msgs.Vector3Msg(angularVelocity.x, angularVelocity.y, angularVelocity.z);

        ros.Publish(odomTopic, odomMsg);
    }

    private void OnDestroy()
    {
        if (ros != null)
        {
            ros.Disconnect();
        }
    }
}
```

## Environment Creation and Interaction

### Creating Interactive Environments

Unity excels at creating rich, interactive environments for robot testing:

```csharp
using UnityEngine;
using System.Collections.Generic;

public class InteractiveEnvironment : MonoBehaviour
{
    [Header("Environment Configuration")]
    [SerializeField] private GameObject[] obstaclePrefabs;
    [SerializeField] private GameObject[] interactiveObjects;
    [SerializeField] private Material[] environmentMaterials;

    [Header("Physics Properties")]
    [SerializeField] private float gravityScale = 1.0f;
    [SerializeField] private PhysicMaterial defaultMaterial;

    [Header("Test Scenarios")]
    [SerializeField] private TestScenario[] testScenarios;

    private List<GameObject> spawnedObjects = new List<GameObject>();

    [System.Serializable]
    public class TestScenario
    {
        public string scenarioName;
        public Vector3 startPosition;
        public Vector3 targetPosition;
        public float difficultyLevel;
        public List<EnvironmentFeature> features;
    }

    [System.Serializable]
    public class EnvironmentFeature
    {
        public string featureType;  // "obstacle", "slope", "narrow_path", etc.
        public Vector3 position;
        public Vector3 scale = Vector3.one;
        public Quaternion rotation = Quaternion.identity;
    }

    void Start()
    {
        CreateEnvironment();
        SetupPhysics();
    }

    private void CreateEnvironment()
    {
        // Create ground plane
        CreateGroundPlane();

        // Add environmental features based on scenarios
        foreach (TestScenario scenario in testScenarios)
        {
            foreach (EnvironmentFeature feature in scenario.features)
            {
                SpawnFeature(feature);
            }
        }

        // Add decorative elements
        AddDecorativeElements();
    }

    private void CreateGroundPlane()
    {
        GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
        ground.name = "Ground";
        ground.transform.SetParent(transform);
        ground.transform.position = Vector3.zero;
        ground.transform.rotation = Quaternion.Euler(-90, 0, 0); // Flat on XZ plane
        ground.transform.localScale = Vector3.one * 10; // 10x10 units

        // Apply material
        if (defaultMaterial != null)
        {
            Renderer groundRenderer = ground.GetComponent<Renderer>();
            if (groundRenderer != null)
            {
                groundRenderer.material = defaultMaterial;
            }
        }

        // Configure physics
        var groundCollider = ground.GetComponent<Collider>();
        if (groundCollider != null)
        {
            groundCollider.material = defaultMaterial;
        }

        spawnedObjects.Add(ground);
    }

    private void SpawnFeature(EnvironmentFeature feature)
    {
        GameObject featureObj = null;

        switch (feature.featureType.ToLower())
        {
            case "obstacle":
                featureObj = CreateObstacle(feature);
                break;
            case "slope":
                featureObj = CreateSlope(feature);
                break;
            case "narrow_path":
                featureObj = CreateNarrowPath(feature);
                break;
            case "stairs":
                featureObj = CreateStairs(feature);
                break;
            default:
                // Try to instantiate from prefab
                if (obstaclePrefabs.Length > 0)
                {
                    GameObject prefab = obstaclePrefabs[Random.Range(0, obstaclePrefabs.Length)];
                    featureObj = Instantiate(prefab, feature.position, feature.rotation);
                }
                break;
        }

        if (featureObj != null)
        {
            featureObj.transform.SetParent(transform);
            featureObj.transform.position = feature.position;
            featureObj.transform.rotation = feature.rotation;
            featureObj.transform.localScale = feature.scale;

            // Add to spawned objects for cleanup
            spawnedObjects.Add(featureObj);
        }
    }

    private GameObject CreateObstacle(EnvironmentFeature feature)
    {
        GameObject obstacle = GameObject.CreatePrimitive(PrimitiveType.Cube);
        obstacle.name = "Obstacle";

        // Configure physics
        var rb = obstacle.AddComponent<Rigidbody>();
        rb.mass = 10f;
        rb.useGravity = true;
        rb.isKinematic = false;

        // Apply material
        if (defaultMaterial != null)
        {
            Renderer rend = obstacle.GetComponent<Renderer>();
            if (rend != null)
            {
                rend.material = defaultMaterial;
            }
        }

        return obstacle;
    }

    private GameObject CreateSlope(EnvironmentFeature feature)
    {
        GameObject slope = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        slope.name = "Slope";

        // Orient as a slope
        slope.transform.rotation = Quaternion.Euler(0, 0, 45); // 45 degree incline
        slope.transform.localScale = new Vector3(0.1f, feature.scale.y, feature.scale.x); // Adjust for slope shape

        // Configure physics
        var rb = slope.AddComponent<Rigidbody>();
        rb.mass = 50f; // Heavy slope
        rb.useGravity = false; // Fixed in place
        rb.isKinematic = true;

        return slope;
    }

    private GameObject CreateNarrowPath(EnvironmentFeature feature)
    {
        // Create narrow path by placing obstacles on sides
        GameObject pathMarker = new GameObject("NarrowPath");

        // Create left barrier
        GameObject leftBarrier = GameObject.CreatePrimitive(PrimitiveType.Cube);
        leftBarrier.name = "LeftBarrier";
        leftBarrier.transform.SetParent(pathMarker.transform);
        leftBarrier.transform.position = feature.position + Vector3.left * (feature.scale.x / 2 + 0.5f);
        leftBarrier.transform.localScale = new Vector3(0.2f, feature.scale.y, feature.scale.z);

        // Create right barrier
        GameObject rightBarrier = GameObject.CreatePrimitive(PrimitiveType.Cube);
        rightBarrier.name = "RightBarrier";
        rightBarrier.transform.SetParent(pathMarker.transform);
        rightBarrier.transform.position = feature.position + Vector3.right * (feature.scale.x / 2 + 0.5f);
        rightBarrier.transform.localScale = new Vector3(0.2f, feature.scale.y, feature.scale.z);

        // Apply materials and physics
        foreach (GameObject barrier in new GameObject[] { leftBarrier, rightBarrier })
        {
            var rb = barrier.AddComponent<Rigidbody>();
            rb.useGravity = false;
            rb.isKinematic = true;

            if (defaultMaterial != null)
            {
                Renderer rend = barrier.GetComponent<Renderer>();
                if (rend != null)
                {
                    rend.material = defaultMaterial;
                }
            }
        }

        return pathMarker;
    }

    private GameObject CreateStairs(EnvironmentFeature feature)
    {
        GameObject stairs = new GameObject("Stairs");

        int steps = Mathf.RoundToInt(feature.scale.y / 0.2f); // Assume 0.2m step height
        float stepDepth = feature.scale.x / steps;

        for (int i = 0; i < steps; i++)
        {
            GameObject step = GameObject.CreatePrimitive(PrimitiveType.Cube);
            step.name = $"Step_{i}";
            step.transform.SetParent(stairs.transform);

            float xPos = (i - steps/2) * stepDepth + feature.scale.x/2;
            float yPos = i * 0.2f + 0.1f; // Half step height offset
            float zPos = 0;

            step.transform.position = feature.position + new Vector3(xPos, yPos, zPos);
            step.transform.localScale = new Vector3(stepDepth * 0.8f, 0.2f, feature.scale.z * 0.8f);

            // Configure physics
            var rb = step.AddComponent<Rigidbody>();
            rb.useGravity = false;
            rb.isKinematic = true;

            if (defaultMaterial != null)
            {
                Renderer rend = step.GetComponent<Renderer>();
                if (rend != null)
                {
                    rend.material = defaultMaterial;
                }
            }
        }

        return stairs;
    }

    private void AddDecorativeElements()
    {
        // Add some decorative elements to make environment visually interesting
        int decorationCount = 10;

        for (int i = 0; i < decorationCount; i++)
        {
            if (obstaclePrefabs.Length > 0)
            {
                GameObject prefab = obstaclePrefabs[Random.Range(0, obstaclePrefabs.Length)];
                Vector3 randomPos = new Vector3(
                    Random.Range(-20f, 20f),
                    0.5f,
                    Random.Range(-20f, 20f)
                );

                GameObject decoration = Instantiate(prefab, randomPos, Quaternion.identity);
                decoration.transform.SetParent(transform);
                decoration.name = $"Decoration_{i}";

                // Make kinematic so it doesn't interfere with physics
                Rigidbody rb = decoration.GetComponent<Rigidbody>();
                if (rb != null)
                {
                    rb.isKinematic = true;
                }

                spawnedObjects.Add(decoration);
            }
        }
    }

    private void SetupPhysics()
    {
        // Configure global physics settings
        Physics.gravity = new Vector3(0, -9.81f * gravityScale, 0);

        // Set default physics material if provided
        if (defaultMaterial != null)
        {
            Physics.defaultMaterial = defaultMaterial;
        }
    }

    public void ResetEnvironment()
    {
        // Remove all spawned objects except the ground
        List<GameObject> objectsToRemove = new List<GameObject>();

        foreach (GameObject obj in spawnedObjects)
        {
            if (obj != null && obj.name != "Ground")
            {
                objectsToRemove.Add(obj);
            }
        }

        foreach (GameObject obj in objectsToRemove)
        {
            spawnedObjects.Remove(obj);
            if (obj != null)
            {
                DestroyImmediate(obj);
            }
        }

        // Recreate environment
        CreateEnvironment();
    }

    private void OnDestroy()
    {
        // Clean up spawned objects
        foreach (GameObject obj in spawnedObjects)
        {
            if (obj != null && obj.name != "Ground")
            {
                DestroyImmediate(obj);
            }
        }
        spawnedObjects.Clear();
    }
}
```

## Performance Optimization for Complex Scenes

### Managing Large Environments

For complex humanoid simulation environments, performance optimization is crucial:

```csharp
using UnityEngine;
using System.Collections.Generic;
using Unity.Jobs;
using Unity.Burst;
using Unity.Collections;

public class PerformanceOptimizer : MonoBehaviour
{
    [Header("LOD Settings")]
    [SerializeField] private float lodDistanceNear = 5f;
    [SerializeField] private float lodDistanceMedium = 15f;
    [SerializeField] private float lodDistanceFar = 30f;

    [Header("Occlusion Settings")]
    [SerializeField] private LayerMask occlusionMask = -1;

    [Header("Batching Settings")]
    [SerializeField] private bool useDynamicBatching = true;
    [SerializeField] private bool useStaticBatching = true;

    private Dictionary<Renderer, LODGroup> rendererLODs = new Dictionary<Renderer, LODGroup>();
    private List<Renderer> allRenderers = new List<Renderer>();

    void Start()
    {
        FindAllRenderers();
        SetupLODSystems();
        OptimizeSceneSettings();
    }

    void Update()
    {
        UpdateLODForViewers();
    }

    private void FindAllRenderers()
    {
        // Find all renderers in the scene that are candidates for optimization
        Renderer[] renderers = FindObjectsOfType<Renderer>();

        foreach (Renderer renderer in renderers)
        {
            // Skip UI elements and other special objects
            if (renderer.CompareTag("UI") || renderer.CompareTag("Player"))
            {
                continue;
            }

            allRenderers.Add(renderer);
        }
    }

    private void SetupLODSystems()
    {
        // Create LOD groups for objects that support it
        foreach (Renderer renderer in allRenderers)
        {
            // Check if renderer is part of a complex model that would benefit from LOD
            if (renderer.sharedMaterials.Length > 1 ||
                renderer.bounds.size.magnitude > 2.0f) // Only for larger objects
            {
                // Create LOD group
                LODGroup lodGroup = renderer.gameObject.AddComponent<LODGroup>();

                // Define LOD levels
                LOD[] lods = new LOD[3];

                // LOD 0: High detail (full quality)
                lods[0] = new LOD(0.5f, renderer.GetComponentsInChildren<Renderer>()); // This is simplified

                // LOD 1: Medium detail (simplified geometry)
                // In practice, you'd have different mesh renderers for each LOD level

                // LOD 2: Low detail (bounding box or icon)
                // This would be a very simplified representation

                lodGroup.SetLODs(lods);
                lodGroup.RecalculateBounds();

                rendererLODs[renderer] = lodGroup;
            }
        }
    }

    private void UpdateLODForViewers()
    {
        // Get all active cameras (main camera, robot cameras, etc.)
        Camera[] cameras = Camera.allCameras;

        foreach (Camera cam in cameras)
        {
            // Only optimize for cameras that are actively rendering the scene
            if (cam.name.Contains("Main") || cam.name.Contains("Robot") || cam.name.Contains("Scene"))
            {
                UpdateLODForCamera(cam);
            }
        }
    }

    private void UpdateLODForCamera(Camera camera)
    {
        Vector3 cameraPos = camera.transform.position;

        foreach (Renderer renderer in allRenderers)
        {
            float distance = Vector3.Distance(cameraPos, renderer.bounds.center);

            // Determine appropriate LOD level based on distance
            LODGroup lodGroup;
            if (rendererLODs.TryGetValue(renderer, out lodGroup))
            {
                // Set the fade mode and update LOD
                if (distance < lodDistanceNear)
                {
                    lodGroup.FadeMode = LODFadeMode.CrossFade;
                    lodGroup.animateCrossFading = true;
                }
                else if (distance < lodDistanceMedium)
                {
                    lodGroup.FadeMode = LODFadeMode.CrossFade;
                    lodGroup.animateCrossFading = true;
                }
                else
                {
                    lodGroup.FadeMode = LODFadeMode.None;
                }

                // Update the LOD group to reflect current distance
                lodGroup.RecalculateBounds();
            }
        }
    }

    private void OptimizeSceneSettings()
    {
        // Configure Unity's built-in optimizations

        // Set up occlusion culling
        if (useDynamicBatching)
        {
            QualitySettings.pixelLightCount = 2; // Limit pixel lights for performance
        }

        // Configure shadow settings for performance
        QualitySettings.shadowProjection = ShadowProjection.StableFit;
        QualitySettings.shadowCascades = 2;
        QualitySettings.shadowDistance = 50f; // Reasonable distance for humanoid simulation

        // Configure texture streaming
        QualitySettings.streamingMipmapsActive = true;
        QualitySettings.streamingMipmapsMaxLevelReduction = 2;
        QualitySettings.streamingMipmapsMaxFileIORequests = 1024;

        // Set up multi-threaded rendering if supported
        if (SystemInfo.supportsMultithreadedRendering)
        {
            QualitySettings.renderingThreadingMode = RenderingThreadingMode.MultiThreaded;
        }
    }

    public void OptimizeForRobotView()
    {
        // Specific optimizations for robot's view/camera
        // Reduce quality settings for robot cameras to maintain performance

        QualitySettings.shadowResolution = ShadowResolution.Low;
        QualitySettings.shadowDistance = 15f; // Closer shadows for robot view
        QualitySettings.anisotropicFiltering = AnisotropicFiltering.Enable;

        // Reduce post-processing effects on robot cameras
        // This would involve finding robot cameras and disabling heavy effects
    }

    public void OptimizeForPresentationView()
    {
        // Restore higher quality settings for presentation/demo views
        QualitySettings.shadowResolution = ShadowResolution.High;
        QualitySettings.shadowDistance = 50f;
        QualitySettings.anisotropicFiltering = AnisotropicFiltering.ForceEnable;
    }
}
```

## Hands-on Lab: Creating a Complete Simulation Environment

Let's create a complete example scene that demonstrates all the concepts:

**Unity Scene Setup Script:**
```csharp
using UnityEngine;
using UnityEngine.SceneManagement;

public class SimulationEnvironmentSetup : MonoBehaviour
{
    [Header("Robot Configuration")]
    [SerializeField] private GameObject robotPrefab;
    [SerializeField] private Vector3 robotStartPosition = new Vector3(0, 1, 0);

    [Header("Environment Configuration")]
    [SerializeField] private GameObject environmentPrefab;
    [SerializeField] private Light mainLight;

    [Header("Simulation Controls")]
    [SerializeField] private bool autoStartSimulation = true;
    [SerializeField] private float simulationSpeed = 1.0f;

    private GameObject instantiatedRobot;
    private GameObject instantiatedEnvironment;

    void Start()
    {
        SetupScene();

        if (autoStartSimulation)
        {
            StartSimulation();
        }
    }

    private void SetupScene()
    {
        // Set up lighting
        SetupLighting();

        // Create environment
        if (environmentPrefab != null)
        {
            instantiatedEnvironment = Instantiate(environmentPrefab, Vector3.zero, Quaternion.identity);
            instantiatedEnvironment.name = "SimulationEnvironment";
        }
        else
        {
            // Create basic environment if none provided
            instantiatedEnvironment = CreateBasicEnvironment();
        }

        // Spawn robot
        if (robotPrefab != null)
        {
            instantiatedRobot = Instantiate(robotPrefab, robotStartPosition, Quaternion.identity);
            instantiatedRobot.name = "HumanoidRobot";

            // Configure robot for simulation
            ConfigureRobotForSimulation(instantiatedRobot);
        }

        // Set up physics
        SetupPhysicsConfiguration();

        // Set up camera
        SetupMainCamera();

        Debug.Log("Simulation environment set up successfully!");
    }

    private void SetupLighting()
    {
        if (mainLight == null)
        {
            // Create a main light if none provided
            GameObject lightObj = new GameObject("Main Light");
            mainLight = lightObj.AddComponent<Light>();
            mainLight.type = LightType.Directional;
            mainLight.color = Color.white;
            mainLight.intensity = 1.0f;
            mainLight.transform.position = new Vector3(10, 10, -10);
            mainLight.transform.LookAt(Vector3.zero);
        }
        else
        {
            mainLight.transform.LookAt(Vector3.zero);
        }

        // Set up reflection probes for realistic lighting
        SetupReflectionProbes();
    }

    private void SetupReflectionProbes()
    {
        // Create reflection probes for realistic lighting on robot
        var reflectionProbe = gameObject.AddComponent<ReflectionProbe>();
        reflectionProbe.mode = ReflectionProbeMode.Realtime;
        reflectionProbe.size = new Vector3(20, 20, 20);
        reflectionProbe.center = Vector3.zero;
        reflectionProbe.importance = 1;
        reflectionProbe.resolution = 128;
    }

    private GameObject CreateBasicEnvironment()
    {
        GameObject env = new GameObject("BasicEnvironment");

        // Create ground
        GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
        ground.name = "Ground";
        ground.transform.SetParent(env.transform);
        ground.transform.position = Vector3.zero;
        ground.transform.rotation = Quaternion.Euler(-90, 0, 0);
        ground.transform.localScale = Vector3.one * 5;

        // Add some basic obstacles
        for (int i = 0; i < 5; i++)
        {
            GameObject obstacle = GameObject.CreatePrimitive(PrimitiveType.Cube);
            obstacle.name = $"Obstacle_{i}";
            obstacle.transform.SetParent(env.transform);

            float x = Random.Range(-8f, 8f);
            float z = Random.Range(-8f, 8f);
            obstacle.transform.position = new Vector3(x, 0.5f, z);

            // Random size
            float size = Random.Range(0.5f, 2f);
            obstacle.transform.localScale = Vector3.one * size;
        }

        return env;
    }

    private void ConfigureRobotForSimulation(GameObject robot)
    {
        // Add essential components for simulation
        var rosBridge = robot.AddComponent<UnityROSBridge>();
        var animController = robot.AddComponent<HumanoidAnimationController>();
        var collisionOptimizer = robot.AddComponent<CollisionOptimizer>();

        // Configure physics
        var rigidbodies = robot.GetComponentsInChildren<Rigidbody>();
        foreach (var rb in rigidbodies)
        {
            rb.interpolation = RigidbodyInterpolation.Interpolate;
            rb.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;
        }
    }

    private void SetupPhysicsConfiguration()
    {
        // Configure global physics for humanoid simulation
        Physics.defaultSolverIterations = 10;  // Balance between performance and accuracy
        Physics.defaultSolverVelocityIterations = 8;
        Physics.sleepThreshold = 0.001f;
        Physics.maxAngularVelocity = 50f;
    }

    private void SetupMainCamera()
    {
        Camera mainCam = Camera.main;
        if (mainCam == null)
        {
            // Create main camera if none exists
            GameObject camObj = new GameObject("Main Camera");
            mainCam = camObj.AddComponent<Camera>();
            mainCam.tag = "MainCamera";
        }

        // Position camera to view the robot
        mainCam.transform.position = new Vector3(5, 3, -5);
        mainCam.transform.LookAt(robotStartPosition);

        // Set up camera for optimal viewing
        mainCam.fieldOfView = 60f;
        mainCam.nearClipPlane = 0.1f;
        mainCam.farClipPlane = 100f;
    }

    public void StartSimulation()
    {
        Time.timeScale = simulationSpeed;

        Debug.Log($"Simulation started at speed: {simulationSpeed}x");

        // Send message to robot to start its control loop
        if (instantiatedRobot != null)
        {
            instantiatedRobot.SendMessage("StartControlLoop", SendMessageOptions.DontRequireReceiver);
        }
    }

    public void PauseSimulation()
    {
        Time.timeScale = 0f;
        Debug.Log("Simulation paused");
    }

    public void ResumeSimulation()
    {
        Time.timeScale = simulationSpeed;
        Debug.Log($"Simulation resumed at speed: {simulationSpeed}x");
    }

    public void ResetSimulation()
    {
        // Reset robot position
        if (instantiatedRobot != null)
        {
            instantiatedRobot.transform.position = robotStartPosition;
            instantiatedRobot.transform.rotation = Quaternion.identity;

            // Reset all joint positions (if using articulation bodies)
            var articulationBodies = instantiatedRobot.GetComponentsInChildren<ArticulationBody>();
            foreach (var body in articulationBodies)
            {
                body.Sleep();
            }
        }

        Debug.Log("Simulation reset");
    }

    public void SetSimulationSpeed(float speed)
    {
        simulationSpeed = Mathf.Clamp(speed, 0.1f, 5.0f);
        Time.timeScale = simulationSpeed;
        Debug.Log($"Simulation speed set to: {simulationSpeed}x");
    }

    void OnDestroy()
    {
        // Cleanup
        if (instantiatedRobot != null)
        {
            Destroy(instantiatedRobot);
        }
        if (instantiatedEnvironment != null)
        {
            Destroy(instantiatedEnvironment);
        }
    }
}
```

## Evaluation Checkpoints

1. How do you configure Unity for realistic humanoid physics simulation?
2. What are the key components needed for ROS2 integration with Unity?
3. How do you optimize Unity scenes for complex humanoid robot simulation?
4. What are the best practices for collision detection with multi-link robots?
5. How do you visualize sensor data in real-time within Unity?

## Troubleshooting Unity Simulation Issues

### Common Performance Issues
- **Slow simulation**: Reduce physics substeps, simplify collision meshes, use LOD
- **Jittery movement**: Increase physics FPS, use interpolation, check mass ratios
- **Penetrating collisions**: Increase solver iterations, adjust material properties, reduce timesteps

### Physics Issues
- **Objects falling through surfaces**: Check collision layers, material properties, and mesh normals
- **Unrealistic bouncing**: Adjust restitution coefficients and contact settings
- **Stability problems**: Balance mass ratios, adjust damping, tune joint limits

### ROS Communication Issues
- **Connection failures**: Verify IP addresses, port availability, firewall settings
- **Topic mismatches**: Check topic names and message types
- **Latency issues**: Optimize publish rates, reduce message sizes, use efficient serialization

## Summary

Unity provides a powerful platform for creating advanced digital twin environments for humanoid robotics. Its combination of realistic physics simulation, advanced rendering capabilities, and flexible architecture makes it ideal for developing sophisticated simulation environments.

The integration with ROS2 through the ROS-TCP-Connector enables bidirectional communication between Unity and the broader ROS ecosystem, allowing for realistic simulation of robot behaviors, sensor data, and environmental interactions.

Key considerations for Unity-based humanoid simulation include:
- Proper physics configuration for realistic robot dynamics
- Performance optimization for complex multi-link robots
- Real-time sensor data visualization
- Efficient collision detection and contact handling
- Seamless ROS2 integration for real-world transfer

With these capabilities, Unity becomes an invaluable tool in the development and testing of humanoid robots, bridging the gap between simulation and reality.