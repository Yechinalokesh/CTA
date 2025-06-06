
class FaceRecognitionSystem:
    def __init__(self, voice_ai_speak_func=None, gui_set_expression_func=None,
                 gui_update_webcam_func=None, shutdown_event=None):
        self.voice_ai_speak_func = voice_ai_speak_func
        self.gui_set_expression_func = gui_set_expression_func
        self.gui_update_webcam_func = gui_update_webcam_func
        self.shutdown_event = shutdown_event if shutdown_event else threading.Event()

        self.known_faces_dir = "src/known_faces"
        self.log_file_path = "src/face_recognition_log.csv"

        self.known_face_encodings = []
        self.known_face_names = []
        self.greeted_today = set()
        self.last_greet_reset_date = date.today() # For daily reset of greetings
        self.known_faces_lock = threading.Lock() # Lock for known_face_encodings and known_face_names

        self.log_file = None
        self.log_writer = None
        self.video_capture = None # For the continuous recognition loop
        self.camera_access_lock = threading.Lock() # To manage access between continuous loop and on-demand functions

        self._load_known_faces()
        self._open_log_file()


