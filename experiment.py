# -*- coding: utf-8 -*-
# Written as a direct replication of Callejas et al (2004),
# intended for use as a lab demonstration in PSYO/NESC 3131 (Fall, 2019)

__author__ = "Brett Feltmate"

# Import necessary packages & utilities
import klibs
from klibs                      import P
from klibs.KLAudio              import Tone
from klibs.KLUserInterface      import any_key
from klibs.KLCommunication      import message
from klibs.KLGraphics           import KLDraw as kld
from klibs.KLGraphics           import fill, flip, blit
from klibs.KLResponseCollectors import KeyPressResponse
from klibs.KLUtilities          import deg_to_px, hide_mouse_cursor

import random

# RGB constants for convenience
WHITE = [255, 255, 255, 255]
BLACK = [0, 0, 0, 255]
GREY =  [128, 128, 128, 255]


class ANTi(klibs.Experiment):

    def setup(self):

        # Stimulus sizes
        fixation_size =      deg_to_px(0.32)
        fixation_thickness = deg_to_px(0.08)
        cue_size =           deg_to_px(0.64)
        cue_thickness =      deg_to_px(0.08)
        arrow_tail_len =     deg_to_px(0.48)
        arrow_tail_width =   deg_to_px(0.15)
        arrow_head_len =     deg_to_px(0.25)
        arrow_head_width =   deg_to_px(0.45, even=True)
        arrow_dimensions =   [arrow_tail_len, arrow_tail_width,
                              arrow_head_len, arrow_head_width]

        # Stimuli
        self.warning_tone = Tone(50, 'sine', frequency=2000, volume=0.5)
        self.fixation =     kld.FixationCross(fixation_size, fixation_thickness, fill=WHITE)
        self.cue =          kld.Asterisk(cue_size, thickness=cue_thickness, fill=WHITE, spokes=8)

        self.arrow_r =      kld.Arrow(*arrow_dimensions, fill=WHITE)
        self.arrow_l =      kld.Arrow(*arrow_dimensions, fill=WHITE, rotation=180)
        self.arrow_r.render()
        self.arrow_l.render()

        # Layout
        self.height_offset =    deg_to_px(1.3)
        self.flanker_offset =   arrow_tail_len + arrow_head_len + deg_to_px(0.16)
        self.above_loc =        (P.screen_c[0], P.screen_c[1] - self.height_offset)
        self.below_loc =        (P.screen_c[0], P.screen_c[1] + self.height_offset)
        self.cue_locations =    {'above': self.above_loc, 'below': self.below_loc}

        # Insert practice block (when applicable)
        if P.run_practice_blocks:
            self.insert_practice_block(block_nums=1, trial_counts=24)

        self.instructions_presented = False

    def block(self):
        # Grab 1/2 mark
        halfway_block = P.blocks_per_experiment / 2 + 1

        # Present task instructions prior to 1st block
        if not self.instructions_presented:
            self.instructions_presented = True
            halfway_block += 1
            txt = (
                "During this task arrows will appear either above or below fixation.\n"
                "Your job is to indicate in which direction the middle arrow is pointing,\n"
                "both as quickly and accurately as possible.\n"
                "( 'c' = Left, 'm' = Right )\n\n"
                "Press any key to continue..."
            )

            msg = message(txt, align='center', blit_txt=False)

            fill()
            blit(msg, registration=5, location=P.screen_c)
            flip()

            # Instructions will hang until keypress
            any_key()

        # Provide break at 1/2 mark
        if P.block_number == halfway_block:
            txt = ("You're half way through! Take a break and\n"
                   "press any key when you're ready to continue.")

            msg = message(txt, align='center', blit_txt=False)

            fill()
            blit(msg, registration=5, location=P.screen_c)
            flip()

            any_key()


    def setup_response_collector(self):
        # Responses made by keypress
        self.rc.uses(KeyPressResponse)
        # Establish 'valid' response values
        self.rc.keypress_listener.key_map = {'c': 'left', 'm': 'right'}
        # 5000ms response window
        self.rc.terminate_after = [5000, klibs.TK_MS]
        # Stimulus display to present during response collection
        self.rc.display_callback = self.rc_callback
        # Terminate response collection on valid response
        self.rc.keypress_listener.interrupts =  True

    def trial_prep(self):
        # Establish cue condition based on cue validity
        if self.cue_type == 'valid':
            self.cue_location = self.target_location

        elif self.cue_type == 'none':
            self.cue_location = None

        else:
            self.cue_location = 'above' if self.target_location == 'below' else 'below'

        # Establish remaining trial factors
        self.target_direction = random.choice(['left', 'right'])
        self.tone_onset =       random.randrange(400, 1650, 50)

        # Generate target & flanker arrows
        self.arrows =           self.generate_arrows()

        # Establish sequence of events
        events = []
        events.append(['tone_on',   self.tone_onset])
        events.append(['tone_off',  events[-1][1] + 50])
        events.append(['cue_on',    events[-1][1] + 350])
        events.append(['cue_off',   events[-1][1] + 50])
        events.append(['target_on', events[-1][1] + 50])

        # Register sequence w/ event manager
        for e in events:
            self.evm.register_ticket(e)

        # Hide cursor during trial
        hide_mouse_cursor()

    def trial(self):
        # Set to true once played (to avoid repeats)
        tone_played = False

        # Prior to target onset, present fixation, tone & cue (when applicable)
        while self.evm.before('target_on'):
            fill()

            blit(self.fixation, registration=5, location=P.screen_c)

            # Tone
            if self.tone_trial and self.evm.between('tone_on', 'tone_off'):
                if not tone_played:
                    self.warning_tone.play()
                    tone_played = True

            # Cue
            if self.cue_location is not None and self.evm.between('cue_on', 'cue_off'):
                loc = self.cue_locations[self.cue_location]
                blit(self.cue, registration=5, location=loc)

            flip()
        # For some reason the cursor reappears here...
        hide_mouse_cursor()

        # Present target
        fill()
        blit(self.fixation, registration=5, location=P.screen_c)
        for shape, loc in self.arrows:
            blit(shape, registration=5, location=loc)
        flip()

        # Listen for response
        self.rc.collect()

        # Record response value & rt
        response, rt = self.rc.keypress_listener.response()
        # If no (valid) response made before timeout
        if rt == klibs.TIMEOUT:
            response = 'na'

        # Label response as correct/incorrect
        accuracy = int(response == self.target_direction)

        # Record trial data to database
        return {
            "block_num":        P.block_number,
            "trial_num":        P.trial_number,
            "practicing":       P.practicing,
            "tone_trial":       self.tone_trial,
            "tone_onset":       self.tone_onset,
            "cue_type":         self.cue_type,
            "congruent":        self.congruent,
            "target_location":  self.target_location,
            "target_direction": self.target_direction,
            "accuracy":         accuracy,
            "response":         response,
            "rt":               rt
        }

    def trial_clean_up(self):
        # Clear response collector
        pass

    def clean_up(self):
        pass

    # Continuously presents targets until response or timeout
    def rc_callback(self):
        fill()

        blit(self.fixation, registration=5, location=P.screen_c)
        for shape, loc in self.arrows:
            blit(shape, registration=5, location=loc)

        flip()

    # Generates target & flanker stimuli
    def generate_arrows(self):

        # Set vertical position of arrows
        if self.target_location == 'above':
            base_height = P.screen_c[1] - self.height_offset
        else:
            base_height = P.screen_c[1] + self.height_offset

        # Set directionality of arrows
        if self.target_direction == 'left':
            target_arrow = self.arrow_l
            flanker_arrow = self.arrow_l if self.congruent else self.arrow_r
        else:
            target_arrow = self.arrow_r
            flanker_arrow = self.arrow_r if self.congruent else self.arrow_l

        # Generate arrows according to the above
        arrows = []
        for offset in [-2, -1, 0, 1, 2]:
            x = P.screen_c[0] + (offset * self.flanker_offset)
            y = base_height
            arrow = (target_arrow if offset == 0 else flanker_arrow, (x, y))
            arrows.append(arrow)

        return arrows
