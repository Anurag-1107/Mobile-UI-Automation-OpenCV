import subprocess
import time
import cv2
import numpy as np
import os
import glob
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# matching confidence
MATCH_THRESHOLD = 0.82

# agar kaafi time tak kuch nahi mila toh back press hoga
BACK_DELAY = 15

# popup close karne ke baad thoda wait
CLICK_DELAY = 1.2


class AndroidUIBot:

    def __init__(self, device_id, total_cycles):

        self.device_id = device_id
        self.total_cycles = total_cycles

        self.check_device()

        # templates load kar lo
        self.start_template = cv2.imread(
            "templates/button_start.png"
        )

        self.next_template = cv2.imread(
            "templates/button_next.png"
        )

        self.close_templates = self.load_close_templates()

    def check_device(self):

        result = subprocess.run(
            "adb devices",
            shell=True,
            capture_output=True,
            text=True
        )

        if self.device_id not in result.stdout:
            raise RuntimeError(
                f"Device {self.device_id} not connected"
            )

        logger.info(f"Connected to device {self.device_id}")

    def load_close_templates(self):

        templates = []

        # saare close button templates load kar lo
        for file in sorted(glob.glob("templates/close*.png")):

            image = cv2.imread(file)

            if image is not None:
                templates.append((file, image))

        logger.info(f"{len(templates)} close templates loaded")

        return templates

    def take_screenshot(self):

        command = (
            f"adb -s {self.device_id} "
            f"exec-out screencap -p"
        )

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True
        )

        if result.returncode != 0:
            return None

        image = cv2.imdecode(
            np.frombuffer(result.stdout, np.uint8),
            cv2.IMREAD_COLOR
        )

        return image

    def tap(self, x, y):

        command = (
            f"adb -s {self.device_id} "
            f"shell input tap {x} {y}"
        )

        subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    def press_back(self):

        command = (
            f"adb -s {self.device_id} "
            f"shell input keyevent 4"
        )

        subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    def find_template(self, screen, template):

        if screen is None or template is None:
            return None

        result = cv2.matchTemplate(
            screen,
            template,
            cv2.TM_CCOEFF_NORMED
        )

        _, confidence, _, location = cv2.minMaxLoc(result)

        if confidence < MATCH_THRESHOLD:
            return None

        h, w = template.shape[:2]

        center_x = location[0] + w // 2
        center_y = location[1] + h // 2

        return center_x, center_y, confidence

    def wait_and_click_start(self):

        logger.info("Waiting for start button")

        while True:

            # current screen ka screenshot le lo
            screen = self.take_screenshot()

            # template match karke button find karenge
            match_data = self.find_template(
                screen,
                self.start_template
            )

            if match_data:

                logger.info("Start button found")

                # button mil gaya toh click kar do
                self.tap(match_data[0], match_data[1])

                return

            time.sleep(1)

    def wait_and_click_next(self):

        logger.info("Waiting for next button")

        while True:

            screen = self.take_screenshot()

            match_data = self.find_template(
                screen,
                self.next_template
            )

            if match_data:

                logger.info("Next button detected")

                self.tap(match_data[0], match_data[1])

                return

            time.sleep(1)

    def close_popups(self):

        logger.info("Scanning screen for popup buttons")

        last_back_time = time.time()

        while True:

            screen = self.take_screenshot()

            if screen is None:
                continue

            # agar start button wapas aa gaya
            # matlab cycle complete ho gaya
            start_found = self.find_template(
                screen,
                self.start_template
            )

            if start_found:

                logger.info("Workflow cycle completed")

                return

            best_match = None
            best_name = None
            best_confidence = 0

            # screen pe close button dhoondo
            for file_name, template in self.close_templates:

                match_data = self.find_template(
                    screen,
                    template
                )

                if match_data:

                    if match_data[2] > best_confidence:

                        best_match = match_data
                        best_name = file_name
                        best_confidence = match_data[2]

            if best_match:

                logger.info(
                    f"Popup closed using {best_name}"
                )

                self.tap(
                    best_match[0],
                    best_match[1]
                )

                last_back_time = time.time()

                time.sleep(CLICK_DELAY)

            else:

                # agar kuch detect nahi hua toh back maar do
                if time.time() - last_back_time > BACK_DELAY:

                    logger.warning(
                        "No popup detected, pressing back"
                    )

                    self.press_back()

                    last_back_time = time.time()

            time.sleep(1)

    def run_workflow(self):

        self.wait_and_click_start()

        self.wait_and_click_next()

        self.close_popups()

    def start(self):

        # pura workflow multiple times chalega
        for cycle in range(1, self.total_cycles + 1):

            logger.info(
                f"Running cycle "
                f"{cycle}/{self.total_cycles}"
            )

            self.run_workflow()

            time.sleep(1)

        logger.info("Finished all cycles")


def main():

    # adb devices se device id copy karo
    device_id = input(
        "Enter device ID: "
    ).strip()

    if not os.path.exists(
        "templates/button_start.png"
    ):

        logger.error(
            "button_start.png missing"
        )

        return

    if not os.path.exists(
        "templates/button_next.png"
    ):

        logger.error(
            "button_next.png missing"
        )

        return

    cycles = int(
        input("Enter number of cycles: ")
    )

    bot = AndroidUIBot(
        device_id,
        cycles
    )

    bot.start()


if __name__ == "__main__":
    main()