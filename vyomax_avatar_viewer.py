import sys
import os
import site

# --- Panda3D Core Imports ---
# It's good practice to put these at the top after standard library imports
try:
    from direct.showbase.ShowBase import ShowBase
    from panda3d.core import (
        Filename, DirectionalLight, AmbientLight, LVecBase4f,
        AnimControlCollection, AutoBind, NodePath, ClockObject
    )
    from direct.task import Task
    from direct.actor.Actor import Actor # For comparison or if GLTF doesn't embed anims directly
    from direct.interval.IntervalGlobal import Sequence, Func, Wait, LerpFunc
    PANDA3D_CORE_AVAILABLE = True
except ImportError as e:
    print(f"❌ CRITICAL ERROR: Could not import core Panda3D modules: {e}")
    print("   Panda3D installation might be broken or not installed.")
    PANDA3D_CORE_AVAILABLE = False
    # exit() # Exit if core Panda3D is missing

# --- Script Start & Environment Info ---
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

if not PANDA3D_CORE_AVAILABLE:
    print("Exiting due to missing core Panda3D components.")
    sys.exit()


class VyomaxAvatarApp(ShowBase):
    def __init__(self):
        super().__init__()
        print("\n--- VyomaxAvatarApp __init__ ---")

        if PANDA3D_GLTF_AVAILABLE:
            try:
                # panda3d_gltf.patch_loader(self.loader) # This is good
                # For more fine-grained control or ensuring it's active:
                panda3d_gltf.patch_loader(self.loader)
                print("🛠️ GLTF loader patched.")
            except Exception as e_patch:
                print(f"🔥 ERROR patching GLTF loader: {e_patch}")
        else:
            print("⚠️ panda3d-gltf not available, GLB models may not load correctly or at all.")
            # Potentially exit if GLTF is essential
            # return

        self.disableMouse()
        self.setBackgroundColor(0.2, 0.2, 0.2, 1) # Darker background for better contrast

        # IMPORTANT: Replace this with the actual path to YOUR model
        # Or place 'me.glb' in a subdirectory 'assets/avatar_faces' relative to this script
        model_path_str = r"C:\Users\lavan\OneDrive\Desktop\Parivartan_Vyomax\assets\avatar_faces\me.glb"
        # Alternatively, for relative path:
        # script_dir = os.path.dirname(os.path.abspath(__file__))
        # model_path_str = os.path.join(script_dir, "assets", "avatar_faces", "me.glb")

        print(f"🔍 Attempting to load model from: {model_path_str}")
        model_path = Filename.fromOsSpecific(model_path_str)

        if not model_path.exists():
            print(f"❌ ERROR: Model file not found at {model_path_str}")
            return

        self.avatar = self.loader.loadModel(model_path)
        if not self.avatar or self.avatar.isEmpty():
            print("❌ ERROR: Failed to load the GLB model. Check path, GLTF setup, and model integrity.")
            return
        print("✅ Model loaded successfully.")

        self.avatar.reparentTo(self.render)
        self.avatar.setScale(1) # Start with 1, adjust if necessary. RPM avatars are usually ~1.8 units tall.
                                # Your original 15 was very large.

        # --- Avatar Orientation ---
        # To stand "straight" and face the camera (which we'll place at Y=-10 or similar):
        # H=180 means rotate 180 degrees around Z (up) axis.
        # P=0 means no pitch (not looking up or down).
        # R=0 means no roll.
        self.avatar.setHpr(180, 0, 0)
        self.avatar.setPos(0, 0, 0) # Place at origin. Adjust Y if model's feet are not at its own origin.

        # --- Camera Setup ---
        self.camera.setPos(0, -5, 1.5) # Closer to the avatar, slightly elevated (assuming avatar height ~1.8m)
        self.camera.lookAt(0, 0, 1) # Look at the approximate head height of the avatar

        # --- Lighting ---
        dlight = DirectionalLight("dlight")
        dlight.setColor(LVecBase4f(0.8, 0.8, 0.7, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(30, -60, 0) # Angled light
        self.render.setLight(dlnp)

        alight = AmbientLight("alight")
        alight.setColor(LVecBase4f(0.3, 0.3, 0.4, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        print("💡 Lighting setup complete.")

        # --- Animations ---
        self.anims = AnimControlCollection()
        # panda3d_gltf automatically finds animations when they are part of the GLTF structure.
        # We still need to bind them to our collection.
        # The `find_anim_control` helper might be what panda3d_gltf uses, or it might
        # populate animations differently. AutoBind is the standard Panda3D way.
        num_anims_found = AutoBind.findAnimations(self.avatar, self.anims)
        print(f"🎬 Found {num_anims_found} animation(s) for the avatar.")

        if self.anims.getNumAnims() > 0:
            print("   Available animations:")
            for anim_name in self.anims.getAnimNames():
                print(f"     - {anim_name}")
            # Try to play an "Idle" or "Breathing" animation if it exists
            # Common names: "Idle", "idle", "T-Pose", "A-Pose", "Breathing", "Standing"
            # For ReadyPlayerMe, it might be something like "F_Standing_Idle_001"
            idle_anim_names = ["Idle", "idle", "F_Standing_Idle_001", "M_Standing_Idle_001", "Standing", "Breathing"]
            played_idle = False
            for name in idle_anim_names:
                if name in self.anims.getAnimNames():
                    self.anims.loop(name, restart=1)
                    print(f"   Looping idle animation: '{name}'")
                    played_idle = True
                    break
            if not played_idle and self.anims.getNumAnims() > 0:
                # Fallback: loop the first animation found if no specific idle is present
                first_anim_name = self.anims.getAnimNames()[0]
                self.anims.loop(first_anim_name, restart=1)
                print(f"   Looping first available animation as idle: '{first_anim_name}'")
        else:
            print("   No animations found embedded in the model for AnimControlCollection.")
            # If animations are separate files (classic Panda3D Actor style):
            # self.avatar = Actor(model_path, {"walk": "path/to/walk.gltf", "wave": "path/to/wave.gltf"})
            # self.avatar.loop("walk")


        # --- Shape Keys / Blend Shapes (for blinking, lip sync) ---
        # panda3d_gltf makes these available via `set_blend_shape_weight`
        self.blend_shape_names = []
        if hasattr(self.avatar, 'get_blend_shape_names'): # Check if the method exists (added by panda3d_gltf)
            self.blend_shape_names = list(self.avatar.get_blend_shape_names())
            if self.blend_shape_names:
                print(f"🎨 Found {len(self.blend_shape_names)} blend shape(s):")
                # for bs_name in self.blend_shape_names:
                #     print(f"     - {bs_name}") # Can be very verbose
            else:
                print("   No blend shapes found on the model.")
        else:
            print("   Model does not have get_blend_shape_names (panda3d_gltf feature).")


        # --- Setup Controls for Animations & Shape Keys ---
        self.setup_controls()

        # Remove the continuous rotation task if you have an idle animation
        # self.taskMgr.add(self.rotate_avatar_task, "RotateAvatarTask")
        print("✨ VyomaxAvatarApp __init__ is ready.")
        print("--- CONTROLS ---")
        print("W: Play 'Wave' animation (if available)")
        print("K: Play 'Kick' or 'Walk' animation (if available)")
        print("B: Trigger eye blink (if 'eyeBlinkLeft/Right' shape keys exist)")
        print("T: Toggle simple talk cycle (if viseme shape keys like 'viseme_AA', 'viseme_IH' exist)")
        print("I: Play 'Idle' animation (if available)")
        print("------------------")

    def set_all_blend_shapes(self, weight):
        """Helper to set all known blend shapes to a specific weight."""
        if hasattr(self.avatar, 'set_blend_shape_weight'):
            for name in self.blend_shape_names:
                self.avatar.set_blend_shape_weight(name, weight)

    def set_visemes_zero(self):
        """Set all viseme-related blend shapes to 0."""
        if hasattr(self.avatar, 'set_blend_shape_weight'):
            for name in self.blend_shape_names:
                if name.lower().startswith("viseme_"):
                    self.avatar.set_blend_shape_weight(name, 0.0)

    def play_animation_if_exists(self, anim_name_options, loop=False):
        if not self.anims or self.anims.getNumAnims() == 0:
            print(f"No animations available to play '{anim_name_options}'.")
            return False

        for anim_name in anim_name_options:
            if anim_name in self.anims.getAnimNames():
                print(f"Playing animation: '{anim_name}' (Loop: {loop})")
                if loop:
                    self.anims.loop(anim_name, restart=1)
                else:
                    self.anims.play(anim_name)
                    # To return to idle after a one-shot animation:
                    # Find the currently looped animation, stop the one-shot, then re-loop idle.
                    # This is more complex; for now, just play.
                    # A robust way is to use animation layers or Sequence intervals.
                return True
        print(f"Animations '{anim_name_options}' not found.")
        return False

    def blink_eyes(self):
        if not hasattr(self.avatar, 'set_blend_shape_weight'):
            print("Blink: set_blend_shape_weight not available.")
            return

        blink_left_options = ["eyeBlinkLeft", "EyeBlinkLeft", "EyesBlinkLeft", "blendShape1.blnk_L"]
        blink_right_options = ["eyeBlinkRight", "EyeBlinkRight", "EyesBlinkRight", "blendShape1.blnk_R"]

        actual_blink_left = None
        actual_blink_right = None

        for bl_name in blink_left_options:
            if bl_name in self.blend_shape_names:
                actual_blink_left = bl_name
                break
        for br_name in blink_right_options:
            if br_name in self.blend_shape_names:
                actual_blink_right = br_name
                break

        if actual_blink_left and actual_blink_right:
            print(f"Blinking with: {actual_blink_left}, {actual_blink_right}")
            seq = Sequence(
                Func(self.avatar.set_blend_shape_weight, actual_blink_left, 1.0),
                Func(self.avatar.set_blend_shape_weight, actual_blink_right, 1.0),
                Wait(0.15), # Eyes closed duration
                Func(self.avatar.set_blend_shape_weight, actual_blink_left, 0.0),
                Func(self.avatar.set_blend_shape_weight, actual_blink_right, 0.0),
                Wait(0.05), # Small refractory period
                # Optional: Add random delay for next blink in a task
            )
            seq.start()
        else:
            print("Blink shape keys (e.g., 'eyeBlinkLeft', 'eyeBlinkRight') not found.")
            print("Available blend shapes for eyes might be named differently. Check the list.")


    def setup_controls(self):
        self.accept("w", self.play_animation_if_exists, [["Wave", "wave", "F_Wave_001", "M_Wave_001"]])
        self.accept("k", self.play_animation_if_exists, [["Kick", "kick", "Walk", "F_Walk_001"]]) # K for Kick or Walk
        self.accept("i", self.play_animation_if_exists, [["Idle", "idle", "F_Standing_Idle_001", "M_Standing_Idle_001"], True])
        self.accept("b", self.blink_eyes)
        self.accept("t", self.toggle_talk_cycle)

        self.is_talking = False
        self.talk_cycle_task_name = "TalkCycleTask"
        # Common viseme names (especially from ReadyPlayerMe). Your model might differ.
        self.viseme_sequence = [
            "viseme_PP", "viseme_RR", "viseme_AA", "viseme_CH", "viseme_DD", "viseme_E",
            "viseme_FF", "viseme_IH", "viseme_KK", "viseme_nn", "viseme_OH",
            "viseme_O", "viseme_PP", "viseme_SS", "viseme_TH", "viseme_U"
        ]
        self.current_viseme_index = 0

    def toggle_talk_cycle(self):
        if self.is_talking:
            self.taskMgr.remove(self.talk_cycle_task_name)
            self.set_visemes_zero() # Reset mouth to neutral
            self.is_talking = False
            print("Stopped talk cycle.")
        else:
            # Check if at least one viseme from our sequence exists
            can_talk = False
            for v_name_option in self.viseme_sequence:
                if v_name_option in self.blend_shape_names:
                    can_talk = True
                    break
            
            if can_talk and hasattr(self.avatar, 'set_blend_shape_weight'):
                self.taskMgr.add(self.talk_cycle_task, self.talk_cycle_task_name)
                self.is_talking = True
                print("Started talk cycle. (Press 'T' again to stop)")
            else:
                print("Cannot start talk cycle: viseme shape keys (e.g., 'viseme_AA') not found or set_blend_shape_weight unavailable.")

    def talk_cycle_task(self, task):
        self.set_visemes_zero() # Reset previous viseme

        # Get current viseme name from the sequence
        viseme_to_activate = self.viseme_sequence[self.current_viseme_index]

        if viseme_to_activate in self.blend_shape_names:
            self.avatar.set_blend_shape_weight(viseme_to_activate, 1.0)
        else:
            # If a specific viseme isn't found, we could skip or log it
            pass # print(f"Viseme '{viseme_to_activate}' not in model, skipping.")

        self.current_viseme_index = (self.current_viseme_index + 1) % len(self.viseme_sequence)

        task.delayTime = 0.08 # How quickly to switch visemes
        return Task.again

    # def rotate_avatar_task(self, task):
    #     # This was your original rotation task.
    #     # You might want it if you don't have an idle animation.
    #     if hasattr(self, 'avatar') and self.avatar and not self.avatar.isEmpty():
    #          self.avatar.setH(ClockObject.getGlobalClock().getFrameTime() * 20)
    #     return Task.cont

if __name__ == "__main__":
    print("\n--- Running App ---")
    if not PANDA3D_CORE_AVAILABLE:
        print("Cannot run app, core Panda3D modules failed to import.")
    else:
        app = VyomaxAvatarApp()
        # Check if avatar was loaded successfully in __init__
        if hasattr(app, 'avatar') and app.avatar and not app.avatar.isEmpty():
            if hasattr(app, 'win') and app.win:
                app.run()
            else:
                print("Application's ShowBase did not initialize properly (no window). Exiting.")
        else:
            print("Application initialization failed or model did not load. Exiting.")
    print("--- SCRIPT END ---")
