import cv2

print("Scanning for cameras...\n")

found = []
for i in range(5):
    cam = cv2.VideoCapture(i)
    if cam.isOpened():
        ret, frame = cam.read()
        if ret and frame is not None:
            h, w = frame.shape[:2]
            print(f"  [Camera {i}] ✓ Working — resolution: {w}x{h}")
            found.append(i)
            # Save a test snapshot so you can see what each camera sees
            cv2.imwrite(f"camera_{i}_test.jpg", frame)
            print(f"             Snapshot saved: camera_{i}_test.jpg")
        else:
            print(f"  [Camera {i}] Found but couldn't read frame")
        cam.release()
    else:
        print(f"  [Camera {i}] Not found")

print(f"\nWorking cameras: {found}")
if found:
    print(f"To use camera {found[0]}, set: cv2.VideoCapture({found[0]})")