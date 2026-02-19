---
title: USD & Isaac Environment Integration
sidebar_position: 4
description: Integrating Universal Scene Description with NVIDIA Isaac for advanced humanoid simulation
gpu_notes: This chapter requires NVIDIA Isaac Sim; RTX 3080+ or A4000+ recommended for advanced USD scenes
jetson_notes: Isaac Sim not supported on Jetson; requires NVIDIA RTX GPU for rendering and physics
---

# USD & Isaac Environment Integration

## Prerequisites

Before studying this chapter, you should have:
- Understanding of USD (Universal Scene Description) concepts and file formats
- Knowledge of NVIDIA Isaac ecosystem (from previous chapters)
- Experience with 3D scene composition and lighting
- Basic understanding of humanoid robot kinematics and dynamics
- Familiarity with ROS2 integration concepts

## Learning Objectives

By the end of this chapter, you should be able to:
- Create and manipulate USD scenes for humanoid robot simulation
- Integrate USD assets with NVIDIA Isaac Sim for advanced physics
- Configure realistic environments with proper lighting and materials
- Set up complex multi-robot scenarios in Isaac Sim
- Implement advanced sensor simulation using Isaac's capabilities
- Optimize USD scenes for real-time humanoid robot simulation

## Introduction

Universal Scene Description (USD) is Pixar's powerful format for 3D scene interchange, composition, and collaboration. When combined with NVIDIA Isaac Sim, USD becomes the foundation for creating sophisticated digital twin environments for humanoid robots. This integration allows for the creation of photorealistic, physically accurate simulation environments that can bridge the gap between simulation and reality.

NVIDIA Isaac Sim leverages USD as its native scene format, providing seamless integration with the broader Isaac ecosystem. This combination enables the creation of complex humanoid robot simulation scenarios with realistic physics, advanced rendering, and sophisticated sensor simulation capabilities.

## Understanding USD for Robotics

### USD Fundamentals

USD is a scene description format that enables the composition of 3D scenes through a layer-based approach. In robotics applications, USD provides:

1. **Scene Composition**: Ability to combine multiple assets into complex scenes
2. **Layering**: Non-destructive editing through overlay layers
3. **Variant Sets**: Different configurations of the same asset
4. **Animation**: Time-sampled property changes
5. **Materials**: Advanced material definition and assignment

### USD File Structure

A typical USD file structure for robotics:

```usda
#usda 1.0
(
    doc = "Humanoid robot environment with complex scene"
    metersPerUnit = 1
    upAxis = "Y"
)

def Xform "World"
{
    def Xform "Environment"
    {
        def Xform "Floor"
        {
            def Cube "floor_plane"
            {
                extent = [(-10, -0.1, -10), (10, 0.1, 10)]
                prepend primvars:displayColor.timeSamples = { 0: [(0.7, 0.7, 0.7)] }
            }
        }

        def Xform "Obstacles"
        {
            def Capsule "table"
            {
                radius = 0.5
                height = 0.8
                xformOp:translate = (0, 0.4, 2)
            }

            def Sphere "ball"
            {
                radius = 0.2
                xformOp:translate = (1, 0.2, 3)
            }
        }
    }

    def Xform "Robot"
    {
        def Xform "HumanoidRobot"
        {
            # Robot hierarchy would be defined here
            # with proper joint definitions
        }
    }
}
```

### USD ZOO for Robot Assets

NVIDIA Isaac provides the USD ZOO which contains pre-built robot models in USD format:

```python
# Example Python code to load a robot from Isaac ZOO
import omni
from pxr import Usd, UsdGeom, Sdf

def load_humanoid_robot_stage(stage, robot_name, position=(0, 0, 0)):
    """
    Load a humanoid robot from Isaac ZOO into a USD stage
    """
    # Path to Isaac ZOO robot assets
    robot_asset_path = f"omniverse://localhost/NVIDIA/Isaac/4.2.0/Isaac/ZOO/{robot_name}/urdf/{robot_name}.usd"

    # Create a prim for the robot
    robot_prim_path = Sdf.Path(f"/World/{robot_name}")
    robot_prim = stage.DefinePrim(robot_prim_path, "Xform")

    # Apply position transform
    xform_api = UsdGeom.Xformable(robot_prim)
    xform_api.AddTranslateOp().Set(position)

    # Add reference to robot asset
    robot_prim.GetReferences().AddReference(robot_asset_path)

    return robot_prim

def setup_isaac_simulation_environment():
    """
    Set up a complete simulation environment using Isaac Sim
    """
    # Get the stage
    stage = omni.usd.get_context().get_stage()

    # Define the environment
    world_prim = stage.GetPrimAtPath("/World")
    if not world_prim.IsValid():
        world_prim = UsdGeom.Xform.Define(stage, "/World")

    # Add physics scene
    physics_scene = UsdPhysics.Scene.Define(stage, "/World/PhysicsScene")

    # Add gravity
    gravity_api = UsdPhysics.SceneAPI.Apply(physics_scene.GetPrim())
    gravity_api.CreateGravityDirectionAttr().Set(Gf.Vec3f(0.0, -1.0, 0.0))
    gravity_api.CreateGravityMagnitudeAttr().Set(9.81)

    # Load humanoid robot
    humanoid_robot = load_humanoid_robot_stage(
        stage,
        "unitree_a1",  # Example robot from ZOO
        position=(0, 0.5, 0)  # Start 0.5m above ground
    )

    # Configure robot for simulation
    configure_robot_for_simulation(humanoid_robot)

    return stage

def configure_robot_for_simulation(robot_prim):
    """
    Configure robot prim for physics simulation in Isaac Sim
    """
    # Add articulation root
    articulation_root_api = PhysxSchema.PhysxArticulationRootAPI.Apply(robot_prim)

    # Configure articulation root properties
    articulation_root_api.GetEnabledSelfCollisionsAttr().Set(False)

    # Iterate through robot links and configure physics
    for child in robot_prim.GetAllChildren():
        configure_robot_link(child)

def configure_robot_link(link_prim):
    """
    Configure individual robot link for physics simulation
    """
    # Get the link's name to determine its properties
    link_name = link_prim.GetName()

    # Add rigid body component
    rigid_body_api = PhysxSchema.PhysxRigidBodyAPI.Apply(link_prim)
    rigid_body_api.GetLinearDampingAttr().Set(0.05)
    rigid_body_api.GetAngularDampingAttr().Set(0.1)

    # Configure mass based on link type
    if "base" in link_name or "torso" in link_name:
        mass = 10.0
    elif "leg" in link_name or "arm" in link_name:
        mass = 2.0
    elif "foot" in link_name or "hand" in link_name:
        mass = 1.0
    else:
        mass = 0.5

    # Apply mass
    mass_api = PhysxSchema.PhysxMassAPI.Apply(link_prim)
    mass_api.GetMassAttr().Set(mass)

    # Add collision shapes
    add_collision_shapes_to_link(link_prim)

def add_collision_shapes_to_link(link_prim):
    """
    Add appropriate collision shapes to robot link
    """
    # Determine collision shape based on link name
    link_name = link_prim.GetName().lower()

    if "torso" in link_name or "base" in link_name:
        # Use capsule or box for torso
        collision_geom = UsdGeom.Capsule.Define(
            link_prim.GetStage(),
            f"{link_prim.GetPath()}/collision"
        )
        collision_geom.GetAxisAttr().Set("Y")
        collision_geom.GetHeightAttr().Set(0.8)
        collision_geom.GetRadiusAttr().Set(0.15)
    elif "arm" in link_name or "leg" in link_name:
        # Use capsule for limbs
        collision_geom = UsdGeom.Capsule.Define(
            link_prim.GetStage(),
            f"{link_prim.GetPath()}/collision"
        )
        collision_geom.GetAxisAttr().Set("Y")
        collision_geom.GetHeightAttr().Set(0.4)
        collision_geom.GetRadiusAttr().Set(0.05)
    elif "foot" in link_name or "hand" in link_name:
        # Use box for feet/hands
        collision_geom = UsdGeom.Cube.Define(
            link_prim.GetStage(),
            f"{link_prim.GetPath()}/collision"
        )
        collision_geom.GetSizeAttr().Set(0.15)
    else:
        # Use sphere for other links
        collision_geom = UsdGeom.Sphere.Define(
            link_prim.GetStage(),
            f"{link_prim.GetPath()}/collision"
        )
        collision_geom.GetRadiusAttr().Set(0.05)

    # Apply collision properties
    collision_api = PhysxSchema.PhysxCollisionAPI.Apply(collision_geom.GetPrim())
    collision_api.GetContactOffsetAttr().Set(0.02)
    collision_api.GetRestOffsetAttr().Set(0.0)
```

## Isaac Sim Integration

### Setting Up Isaac Sim Environment

NVIDIA Isaac Sim provides a comprehensive simulation environment built on Omniverse. Here's how to set up a humanoid simulation environment:

```python
import carb
import omni
import omni.usd
from pxr import Usd, UsdGeom, Sdf, Gf, UsdPhysics, PhysxSchema
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.utils.prims import get_prim_at_path
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.articulations import Articulation
from omni.isaac.core.utils.viewports import set_camera_view
import numpy as np

class IsaacHumanoidSimulator:
    """
    Class to manage Isaac Sim environment for humanoid robots
    """

    def __init__(self):
        self.world = None
        self.humanoid_robot = None
        self.scene_setup_complete = False

    def setup_environment(self):
        """
        Set up the complete Isaac Sim environment
        """
        # Initialize world
        self.world = World(stage_units_in_meters=1.0)

        # Create stage
        stage = omni.usd.get_context().get_stage()

        # Set up basic scene
        self._setup_basic_scene(stage)

        # Load humanoid robot
        self._load_humanoid_robot()

        # Configure physics
        self._configure_physics()

        # Set up cameras and sensors
        self._setup_cameras_and_sensors()

        self.scene_setup_complete = True
        carb.log_info("Isaac Sim environment setup complete")

    def _setup_basic_scene(self, stage):
        """
        Set up the basic scene with ground, lighting, and physics
        """
        # Create World Xform
        world_prim = stage.GetPrimAtPath("/World")
        if not world_prim.IsValid():
            world_prim = UsdGeom.Xform.Define(stage, "/World")

        # Add ground plane
        self._add_ground_plane(stage)

        # Add basic lighting
        self._add_lighting(stage)

        # Add physics scene
        self._add_physics_scene(stage)

    def _add_ground_plane(self, stage):
        """
        Add a ground plane to the scene
        """
        # Create ground plane
        ground_path = Sdf.Path("/World/ground_plane")
        ground_plane = UsdGeom.Mesh.Define(stage, ground_path)

        # Set up plane geometry
        vertices = [
            Gf.Vec3f(-10.0, 0.0, -10.0),
            Gf.Vec3f(10.0, 0.0, -10.0),
            Gf.Vec3f(10.0, 0.0, 10.0),
            Gf.Vec3f(-10.0, 0.0, 10.0)
        ]

        face_vertex_counts = [4]
        face_vertex_indices = [0, 1, 2, 3]

        ground_plane.GetPointsAttr().Set(vertices)
        ground_plane.GetFaceVertexCountsAttr().Set(face_vertex_counts)
        ground_plane.GetFaceVertexIndicesAttr().Set(face_vertex_indices)

        # Assign material for appearance
        self._assign_material(ground_plane, "ground_material", (0.7, 0.7, 0.7))

        # Add collision for physics
        collision_api = PhysxSchema.PhysxCollisionAPI.Apply(ground_plane.GetPrim())
        collision_api.GetContactOffsetAttr().Set(0.02)
        collision_api.GetRestOffsetAttr().Set(0.0)

    def _add_lighting(self, stage):
        """
        Add basic lighting to the scene
        """
        # Add dome light for ambient lighting
        dome_light_path = Sdf.Path("/World/DomeLight")
        dome_light = UsdLux.DomeLight.Define(stage, dome_light_path)
        dome_light.CreateIntensityAttr(500)
        dome_light.CreateColorAttr(Gf.Vec3f(1.0, 1.0, 1.0))

        # Add directional light for shadows
        directional_light_path = Sdf.Path("/World/DirectionalLight")
        directional_light = UsdLux.DistantLight.Define(stage, directional_light_path)
        directional_light.CreateIntensityAttr(300)
        directional_light.CreateColorAttr(Gf.Vec3f(1.0, 1.0, 1.0))
        directional_light.AddRotateXOp().Set(-45.0)
        directional_light.AddRotateYOp().Set(45.0)

    def _add_physics_scene(self, stage):
        """
        Add physics scene to the USD stage
        """
        physics_scene_path = Sdf.Path("/World/physicsScene")
        physics_scene = UsdPhysics.Scene.Define(stage, physics_scene_path)

        # Set gravity
        gravity_api = UsdPhysics.SceneAPI.Apply(physics_scene.GetPrim())
        gravity_api.CreateGravityDirectionAttr().Set(Gf.Vec3f(0.0, -1.0, 0.0))
        gravity_api.CreateGravityMagnitudeAttr().Set(9.81)

        # Set physics solver parameters
        physics_scene.GetEnableCCDAttr().Set(True)  # Continuous collision detection
        physics_scene.GetUseEnhancedDeterminismAttr().Set(True)

    def _load_humanoid_robot(self):
        """
        Load a humanoid robot into the simulation
        """
        # Path to humanoid robot asset (this would be your specific robot)
        robot_asset_path = "omniverse://localhost/NVIDIA/Isaac/4.2.0/Isaac/Robots/Humanoid/humanoid.usd"

        # Add robot to stage
        robot_path = "/World/HumanoidRobot"
        add_reference_to_stage(
            usd_path=robot_asset_path,
            prim_path=robot_path
        )

        # Create articulation
        self.humanoid_robot = self.world.scene.add(
            Articulation(
                prim_path=robot_path,
                name="humanoid_robot",
                position=np.array([0.0, 1.0, 0.0]),  # Start 1m above ground
                orientation=np.array([1.0, 0.0, 0.0, 0.0])
            )
        )

    def _configure_physics(self):
        """
        Configure physics properties for the robot
        """
        if self.humanoid_robot is not None:
            # Apply default physics settings
            self.humanoid_robot.set_solver_position_iteration_count(16)
            self.humanoid_robot.set_solver_velocity_iteration_count(8)

            # Enable self-collisions if needed
            # self.humanoid_robot.enable_self_collisions(True)

    def _setup_cameras_and_sensors(self):
        """
        Set up cameras and sensors for the simulation
        """
        # Set up viewport camera
        set_camera_view(eye=[5, 5, 5], target=[0, 0, 0])

        # In a real implementation, you would add:
        # - RGB cameras on the robot
        # - Depth sensors
        # - IMU sensors
        # - Force/torque sensors
        # - LIDAR sensors
        pass

    def reset_simulation(self):
        """
        Reset the simulation to initial state
        """
        if self.world is not None:
            self.world.reset()

            # Reset robot position
            if self.humanoid_robot is not None:
                self.humanoid_robot.set_world_poses(
                    positions=np.array([[0.0, 1.0, 0.0]]),
                    orientations=np.array([[1.0, 0.0, 0.0, 0.0]])
                )

    def step_simulation(self, dt=1/60.0):
        """
        Step the simulation forward
        """
        if self.world is not None:
            self.world.step(render=True)

    def run_simulation(self, num_steps=1000):
        """
        Run the simulation for a specified number of steps
        """
        if not self.scene_setup_complete:
            carb.log_error("Scene not set up. Call setup_environment() first.")
            return

        for step in range(num_steps):
            self.step_simulation()

            # Print progress every 100 steps
            if step % 100 == 0:
                carb.log_info(f"Simulation step: {step}/{num_steps}")

        carb.log_info("Simulation completed")
```

## Advanced USD Techniques for Humanoid Simulation

### Creating Complex Environments

For humanoid robots, we often need complex environments with multiple interacting objects:

```python
import omni
from pxr import Usd, UsdGeom, Sdf, Gf, UsdPhysics, PhysxSchema
from omni.isaac.core.utils.stage import add_reference_to_stage
import numpy as np

class ComplexEnvironmentBuilder:
    """
    Builder class for creating complex USD environments for humanoid simulation
    """

    def __init__(self, stage):
        self.stage = stage
        self.world_path = "/World"

    def create_office_environment(self):
        """
        Create a complex office environment with furniture and obstacles
        """
        # Create environment container
        env_path = Sdf.Path(f"{self.world_path}/OfficeEnvironment")
        env_xform = UsdGeom.Xform.Define(self.stage, env_path)

        # Add floor
        self._add_floor(env_path.AppendChild("floor"))

        # Add furniture
        self._add_desk(env_path.AppendChild("desk"), position=(3, 0, 0))
        self._add_chair(env_path.AppendChild("chair"), position=(3.5, 0, 1))
        self._add_bookshelf(env_path.AppendChild("bookshelf"), position=(-2, 0, 2))

        # Add interactive objects
        self._add_door(env_path.AppendChild("door"), position=(5, 0, 0))
        self._add_elevator(env_path.AppendChild("elevator"), position=(-5, 0, -3))

        # Add small objects for manipulation
        self._add_small_objects(env_path.AppendChild("small_objects"))

        return env_xform

    def _add_floor(self, prim_path):
        """
        Add a textured floor to the environment
        """
        floor_mesh = UsdGeom.Mesh.Define(self.stage, prim_path)

        # Define a larger floor
        size = 20  # 20x20 meter floor
        half_size = size / 2

        vertices = [
            Gf.Vec3f(-half_size, 0, -half_size),
            Gf.Vec3f(half_size, 0, -half_size),
            Gf.Vec3f(half_size, 0, half_size),
            Gf.Vec3f(-half_size, 0, half_size)
        ]

        face_vertex_counts = [4]
        face_vertex_indices = [0, 1, 2, 3]

        floor_mesh.GetPointsAttr().Set(vertices)
        floor_mesh.GetFaceVertexCountsAttr().Set(face_vertex_counts)
        floor_mesh.GetFaceVertexIndicesAttr().Set(face_vertex_indices)

        # Add UV coordinates for texturing
        uvs = [
            Gf.Vec2f(0, 0),
            Gf.Vec2f(1, 0),
            Gf.Vec2f(1, 1),
            Gf.Vec2f(0, 1)
        ]
        floor_mesh.GetPrimvar("primvars:st").Set(uvs)

        # Add material
        self._assign_floor_material(floor_mesh)

        # Add collision
        collision_api = PhysxSchema.PhysxCollisionAPI.Apply(floor_mesh.GetPrim())
        collision_api.GetContactOffsetAttr().Set(0.02)
        collision_api.GetRestOffsetAttr().Set(0.0)

    def _add_desk(self, prim_path, position=(0, 0, 0)):
        """
        Add a desk to the environment
        """
        desk_xform = UsdGeom.Xform.Define(self.stage, prim_path)
        desk_xform.AddTranslateOp().Set(Gf.Vec3f(*position))

        # Desk top
        desk_top_path = prim_path.AppendChild("top")
        desk_top = UsdGeom.Cube.Define(self.stage, desk_top_path)
        desk_top.GetSizeAttr().Set(1.5)  # 1.5m x 0.8m x 0.7m
        xform_api = UsdGeom.Xformable(desk_top.GetPrim())
        xform_api.AddScaleOp().Set((1.5, 0.02, 0.8))
        xform_api.AddTranslateOp().Set((0, 0.75, 0))

        # Desk legs
        leg_positions = [(-0.6, 0.35, -0.35), (0.6, 0.35, -0.35), (-0.6, 0.35, 0.35), (0.6, 0.35, 0.35)]
        for i, leg_pos in enumerate(leg_positions):
            leg_path = prim_path.AppendChild(f"leg_{i}")
            leg = UsdGeom.Cylinder.Define(self.stage, leg_path)
            leg.GetRadiusAttr().Set(0.05)
            leg.GetHeightAttr().Set(0.7)

            xform_api = UsdGeom.Xformable(leg.GetPrim())
            xform_api.AddTranslateOp().Set(Gf.Vec3f(*leg_pos))

        # Add materials and physics
        self._assign_wood_material(desk_top)
        self._make_physically_interactable(desk_xform.GetPrim())

    def _add_chair(self, prim_path, position=(0, 0, 0)):
        """
        Add a chair to the environment
        """
        chair_xform = UsdGeom.Xform.Define(self.stage, prim_path)
        chair_xform.AddTranslateOp().Set(Gf.Vec3f(*position))

        # Chair seat
        seat_path = prim_path.AppendChild("seat")
        seat = UsdGeom.Cube.Define(self.stage, seat_path)
        seat.GetSizeAttr().Set(1.0)
        xform_api = UsdGeom.Xformable(seat.GetPrim())
        xform_api.AddScaleOp().Set((0.4, 0.05, 0.4))
        xform_api.AddTranslateOp().Set((0, 0.4, 0))

        # Chair back
        back_path = prim_path.AppendChild("back")
        back = UsdGeom.Cube.Define(self.stage, back_path)
        back.GetSizeAttr().Set(1.0)
        xform_api = UsdGeom.Xformable(back.GetPrim())
        xform_api.AddScaleOp().Set((0.4, 0.4, 0.05))
        xform_api.AddTranslateOp().Set((0, 0.6, -0.18))

        # Chair legs
        leg_positions = [(-0.15, 0.2, -0.15), (0.15, 0.2, -0.15), (-0.15, 0.2, 0.15), (0.15, 0.2, 0.15)]
        for i, leg_pos in enumerate(leg_positions):
            leg_path = prim_path.AppendChild(f"leg_{i}")
            leg = UsdGeom.Cylinder.Define(self.stage, leg_path)
            leg.GetRadiusAttr().Set(0.03)
            leg.GetHeightAttr().Set(0.4)

            xform_api = UsdGeom.Xformable(leg.GetPrim())
            xform_api.AddTranslateOp().Set(Gf.Vec3f(*leg_pos))

        # Add materials and physics
        self._assign_fabric_material(seat)
        self._assign_fabric_material(back)
        self._make_physically_interactable(chair_xform.GetPrim())

    def _add_bookshelf(self, prim_path, position=(0, 0, 0)):
        """
        Add a bookshelf to the environment
        """
        shelf_xform = UsdGeom.Xform.Define(self.stage, prim_path)
        shelf_xform.AddTranslateOp().Set(Gf.Vec3f(*position))

        # Shelf structure
        shelf_dims = (0.8, 2.0, 0.3)  # width, height, depth
        shelf_thickness = 0.02

        # Side panels
        left_panel_path = prim_path.AppendChild("side_left")
        left_panel = UsdGeom.Cube.Define(self.stage, left_panel_path)
        left_panel.GetSizeAttr().Set(1.0)
        xform_api = UsdGeom.Xformable(left_panel.GetPrim())
        xform_api.AddScaleOp().Set((shelf_thickness, shelf_dims[1], shelf_dims[2]))
        xform_api.AddTranslateOp().Set((-shelf_dims[0]/2 + shelf_thickness/2, shelf_dims[1]/2, 0))

        right_panel_path = prim_path.AppendChild("side_right")
        right_panel = UsdGeom.Cube.Define(self.stage, right_panel_path)
        right_panel.GetSizeAttr().Set(1.0)
        xform_api = UsdGeom.Xformable(right_panel.GetPrim())
        xform_api.AddScaleOp().Set((shelf_thickness, shelf_dims[1], shelf_dims[2]))
        xform_api.AddTranslateOp().Set((shelf_dims[0]/2 - shelf_thickness/2, shelf_dims[1]/2, 0))

        # Top panel
        top_panel_path = prim_path.AppendChild("top")
        top_panel = UsdGeom.Cube.Define(self.stage, top_panel_path)
        top_panel.GetSizeAttr().Set(1.0)
        xform_api = UsdGeom.Xformable(top_panel.GetPrim())
        xform_api.AddScaleOp().Set((shelf_dims[0] - 2*shelf_thickness, shelf_thickness, shelf_dims[2]))
        xform_api.AddTranslateOp().Set((0, shelf_dims[1] - shelf_thickness/2, 0))

        # Shelves
        num_shelves = 4
        for i in range(num_shelves):
            shelf_height = (i + 1) * (shelf_dims[1] / (num_shelves + 1))
            shelf_path = prim_path.AppendChild(f"shelf_{i}")
            shelf = UsdGeom.Cube.Define(self.stage, shelf_path)
            shelf.GetSizeAttr().Set(1.0)
            xform_api = UsdGeom.Xformable(shelf.GetPrim())
            xform_api.AddScaleOp().Set((shelf_dims[0] - 2*shelf_thickness, shelf_thickness, shelf_dims[2] - 2*shelf_thickness))
            xform_api.AddTranslateOp().Set((0, shelf_height, 0))

        # Add materials and physics
        self._assign_wood_material(left_panel)
        self._assign_wood_material(right_panel)
        self._assign_wood_material(top_panel)
        for i in range(num_shelves):
            shelf_prim = self.stage.GetPrimAtPath(prim_path.AppendChild(f"shelf_{i}"))
            self._assign_wood_material_direct(shelf_prim)

        self._make_physically_interactable(shelf_xform.GetPrim())

    def _add_small_objects(self, parent_path):
        """
        Add small objects that the humanoid can interact with
        """
        # Add a few books
        for i in range(3):
            book_path = parent_path.AppendChild(f"book_{i}")
            book = UsdGeom.Cube.Define(self.stage, book_path)
            book.GetSizeAttr().Set(1.0)

            xform_api = UsdGeom.Xformable(book.GetPrim())
            xform_api.AddScaleOp().Set((0.15, 0.03, 0.2))
            xform_api.AddTranslateOp().Set(
                Gf.Vec3f(
                    np.random.uniform(-1, 1),
                    0.02,  # Just above ground
                    np.random.uniform(-1, 1)
                )
            )

            # Make physically interactive
            self._make_physically_interactable(book.GetPrim())
            self._assign_paper_material(book)

        # Add a cup
        cup_path = parent_path.AppendChild("cup")
        cup = UsdGeom.Cylinder.Define(self.stage, cup_path)
        cup.GetRadiusAttr().Set(0.04)
        cup.GetHeightAttr().Set(0.1)

        xform_api = UsdGeom.Xformable(cup.GetPrim())
        xform_api.AddTranslateOp().Set(Gf.Vec3f(0.5, 0.05, 0.5))

        self._make_physically_interactable(cup.GetPrim())
        self._assign_ceramic_material(cup)

    def _assign_floor_material(self, geom_prim):
        """
        Assign a realistic floor material
        """
        # This would use Isaac's material system in practice
        # For now, we'll set a simple color
        color_attr = geom_prim.GetDisplayColorAttr()
        color_attr.Set([(0.7, 0.7, 0.7)])

    def _assign_wood_material(self, geom_prim):
        """
        Assign a wood-like material
        """
        color_attr = geom_prim.GetDisplayColorAttr()
        color_attr.Set([(0.6, 0.4, 0.2)])  # Wood color

    def _assign_fabric_material(self, geom_prim):
        """
        Assign a fabric-like material
        """
        color_attr = geom_prim.GetDisplayColorAttr()
        color_attr.Set([(0.8, 0.8, 0.9)])  # Fabric blue

    def _assign_paper_material(self, geom_prim):
        """
        Assign a paper-like material
        """
        color_attr = geom_prim.GetDisplayColorAttr()
        color_attr.Set([(1.0, 1.0, 0.95)])  # Off-white

    def _assign_ceramic_material(self, geom_prim):
        """
        Assign a ceramic-like material
        """
        color_attr = geom_prim.GetDisplayColorAttr()
        color_attr.Set([(0.95, 0.95, 0.95)])  # Near-white

    def _make_physically_interactable(self, prim):
        """
        Make a prim physically interactive with realistic properties
        """
        # Add rigid body properties
        rigid_body_api = PhysxSchema.PhysxRigidBodyAPI.Apply(prim)
        rigid_body_api.GetLinearDampingAttr().Set(0.05)
        rigid_body_api.GetAngularDampingAttr().Set(0.1)

        # Add mass (for dynamic objects)
        mass_api = PhysxSchema.PhysxMassAPI.Apply(prim)
        # Calculate mass based on volume and material density
        # For simple approximation, use default values
        mass_api.GetMassAttr().Set(0.5)  # Default mass for small objects

        # Add collision properties
        collision_api = PhysxSchema.PhysxCollisionAPI.Apply(prim)
        collision_api.GetContactOffsetAttr().Set(0.01)
        collision_api.GetRestOffsetAttr().Set(0.0)

        # Add material properties for friction
        # In practice, this would use USD material definitions