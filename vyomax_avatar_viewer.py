import sys
import os
import site

print("--- SCRIPT START ---")
print(f"Python Executable (sys.executable): {sys.executable}")
print(f"Python Version (sys.version): {sys.version}")
print(f"Operating System: {sys.platform}")
print(f"Current Working Directory (os.getcwd()): {os.getcwd()}")

print("\n--- sys.path ---")
for p in sys.path:
    print(p)
print("----------------\n")

print(f"User Site Packages (site.USER_SITE if hasattr(site, 'USER_SITE') else 'Not available')")
print(f"User Base (site.USER_BASE if hasattr(site, 'USER_BASE') else 'Not available')")

# Check where panda3d core is being loaded from
try:
    import panda3d
    print(f"panda3d core module loaded from: {panda3d.__file__}")
except ImportError:
    print("panda3d core NOT FOUND!")

# Attempt to import panda3d_gltf
PANDA3D_GLTF_AVAILABLE = False
try:
    import panda3d_gltf
    PANDA3D_GLTF_AVAILABLE = True
    print(f"🐼 SUCCESS: panda3d_gltf version {panda3d_gltf.__version__} imported successfully.")
    print(f"   panda3d_gltf module loaded from: {panda3d_gltf.__file__}")
except ImportError as e:
    print(f"❌ IMPORT ERROR: panda3d-gltf module not found. Error: {e}")
    print("   Please install it: pip install panda3d-gltf")
    print("   If already installed, ensure your Python environment (sys.executable above) is correct and matches pip's environment.")
except Exception as e_other:
    print(f"🔥 UNEXPECTED ERROR during panda3d_gltf import: {e_other}")


# Only proceed if ShowBase can be imported
try:
    from direct.showbase.ShowBase import ShowBase
    from panda3d.core import DirectionalLight, AmbientLight, LVecBase4f, Filename
    from direct.task import Task
    PANDA3D_CORE_AVAILABLE = True
except ImportError:
    print("❌ CRITICAL ERROR: Could not import ShowBase or other core Panda3D modules. Panda3D installation might be broken.")
    PANDA3D_CORE_AVAILABLE = False
    # exit() # Exit if core Panda3D is missing

if not PANDA3D_CORE_AVAILABLE:
    print("Exiting due to missing core Panda3D components.")
    exit()


class VyomaxAvatarApp(ShowBase):
    def __init__(self):
        super().__init__()
        print("\n--- VyomaxAvatarApp __init__ ---")

        if PANDA3D_GLTF_AVAILABLE:
            try:
                panda3d_gltf.patch_loader(self.loader)
                print("🛠️ GLTF loader patched.")
            except Exception as e_patch:
                print(f"🔥 ERROR patching GLTF loader: {e_patch}")
        else:
            print("⚠️ panda3d-gltf not available, GLB models may not load correctly or at all.")

        self.disableMouse()

        model_path = r"C:\Users\lavan\OneDrive\Desktop\Parivartan_Vyomax\assets\avatar_faces\me.glb"
        print(f"🔍 Attempting to load model from: {model_path}")

        self.avatar = self.loader.loadModel(Filename.fromOsSpecific(model_path))
        if not self.avatar or self.avatar.isEmpty():
            print("❌ ERROR: Failed to load the GLB model. Check path and GLTF setup.")
            return
        print("✅ Model loaded successfully.")

        self.avatar.reparentTo(self.render)
        self.avatar.setScale(15)
        self.avatar.setHpr(0, -90, 0)
        self.avatar.setPos(0, 0, 0)

        self.camera.setPos(0, -30, 5)
        self.camera.lookAt(self.avatar)

        dlight = DirectionalLight("dlight")
        dlight.setColor(LVecBase4f(0.8, 0.8, 0.8, 1))
        dlight_np = self.render.attachNewNode(dlight)
        dlight_np.setHpr(0, -60, 0)
        self.render.setLight(dlight_np)

        alight = AmbientLight("alight")
        alight.setColor(LVecBase4f(0.3, 0.3, 0.3, 1))
        alight_np = self.render.attachNewNode(alight)
        self.render.setLight(alight_np)
        print("💡 Lighting setup complete.")

        self.taskMgr.add(self.rotate_avatar_task, "RotateAvatarTask")
        print("🔄 Rotation task added.")
        print("✨ VyomaxAvatarApp __init__ is ready.")

    def rotate_avatar_task(self, task):
        if hasattr(self, 'avatar') and self.avatar and not self.avatar.isEmpty():
             self.avatar.setH(self.taskMgr.globalClock.getFrameTime() * 20)
        return Task.cont

if __name__ == "__main__":
    print("\n--- Running App ---")
    app = VyomaxAvatarApp()
    if hasattr(app, 'avatar') and app.avatar and not app.avatar.isEmpty():
        # Check if base was successfully initialized before running
        if hasattr(app, 'win') and app.win: # app.win is a good indicator ShowBase initialized
            app.run()
        else:
            print("Application's ShowBase did not initialize properly. Exiting.")
    else:
        print("Application initialization failed or model did not load. Exiting.")
    print("--- SCRIPT END ---")