import tkinter as tk
from tkinter import *
import time
import math
import random
import numpy as np
import os
import shutil
from PIL import Image,ImageTk

import constants
from players.default_player import Player as DefaultPlayer
from players.team_1 import Player as Player1
from players.team_2 import Player as Player2
from players.team_3 import Player as Player3
from players.team_4 import Player as Player4
from players.team_5 import Player as Player5
from players.team_6 import Player as Player6
from players.team_7 import Player as Player7

from player_state import PlayerState

class Table():
    def __init__(self, id):
        self.id = id
        self.seats = [[-1, -1]] * 10

class WeddingGossip():
    def __init__(self, args):
        # list of player groups
        self.player_teams = args.teams

        if 90 % len(args.teams) != 0:
            print("Inconsistent number of teams")
            return
        
        shutil.rmtree('logs')
        os.mkdir('logs')

        # log file
        self.log = os.path.join("logs", "log.txt")
        self.result = os.path.join("logs", "results.txt")
        self.attendee_logs = []

        with open(self.log, 'w') as f:
            f.write("")

        with open(self.result, 'w') as f:
            f.write("")

        self.num_instances = int(90 // len(args.teams))
        self.player_groups = []

        for team in self.player_teams:
            for i in range(self.num_instances):
                self.player_groups.append(team)

        # list of players
        self.players = []

        # list of player states
        self.player_states = []

        self.shuffled_players = []
        self.shuffled_player_states = []

        # list of tables
        self.tables = []
        for index in range(10):
            self.tables.append(Table(index))

        # list of table ui components
        self.table_comps = []
        self.seat_label_comps = []
        self.id_label_comps = []
        self.turn_eyes_comp = []
        self.left_eyes_comp = []
        self.right_eyes_comp = []
        self.canvas2_text_comp = []
        self.group_score_comp = None
        self.turn_comp = None
        self.group_score_comp = None
        self.check_move = [0] * 90

        self.icons = []

        # number of turns
        self.T = int(args.turns)
        self.turn = 1

        # time interval in ms for gui update
        self.interval = int(args.interval)

        # group score
        self.group_score = 0

        # canvas scale
        self.scale = int(args.scale)

        # list of individual scores
        self.individual_scores = np.zeros(len(self.player_states))

        # checks
        if args.gui == "False" or args.gui == "false":
            self.gui = False
        elif args.gui == "True" or args.gui == "true":
            self.gui = True
            self.root = tk.Tk()
            self.root2=tk.Tk()

        # game state
        self.game_state = "resume"

        # ui angle config
        self.right_talk_angle = [[18, 324], [54, 324], [90, 324], [126, 324], [162, 324], [198, 324], [234, 324], [270, 324], [306, 324], [342, 324]]
        self.left_talk_angle = [[198, 324], [234, 324], [270, 324], [306, 324], [342, 324], [18, 324], [54, 324], [90, 324], [126, 324], [162, 324]]
        self.right_listen_angle = [[18, 359], [54, 359], [90, 359], [126, 359], [162, 359], [198, 359], [234, 359], [270, 359], [306, 359], [342, 359]]
        self.left_listen_angle = [[198, 359], [234, 359], [270, 359], [306, 359], [342, 359], [18, 359], [54, 359], [90, 359], [126, 359], [162, 359]]


        shutil.rmtree('logs')
        os.mkdir("logs")

        # seed
        random.seed(int(args.seed))

        # log files
        self.log = os.path.join("logs", "logs.txt")
        
        with open(self.log, 'w') as f:
            f.write("Logs\n")

        self._game_config(self.player_groups)
        if args.gui == "True" or args.gui == "true":
            self._render_frame()
            self.root.mainloop()
            self.root2.mainloop()
        else:
            self._play_game()

    def _game_config(self, players):
        total_seats = list(range(100))
        assigned_seats = random.sample(total_seats, 90)

        gossips = list(range(1, 91))
        random.shuffle(gossips)

        colors = ['#808080' ,'#ff0000', '#ff8000', '#ffff00', '#80ff00', '#00ffff', '#0000ff', '#8000ff', '#ff00ff', '#800040', '#804000', '#808000', '#408000', '#008080', '#800080']

        attendees = list(range(0, 90))
        random.shuffle(attendees)

        for index, player in enumerate(players):
            id = attendees[index]
            team_num = int(player)
            table_num = assigned_seats[index] // 10
            seat_num = assigned_seats[index] % 10
            gossip = gossips[index]
            color = colors[team_num]

            self.group_score += gossip

            self.tables[table_num].seats[seat_num] = [id, team_num]

            if team_num == 1:
                self.shuffled_players.append(Player1(id, team_num, table_num, seat_num, gossip, color, self.T))
                self.shuffled_player_states.append(PlayerState(id, team_num, table_num, seat_num, gossip, color))
            elif team_num == 2:
                self.shuffled_players.append(Player2(id, team_num, table_num, seat_num, gossip, color, self.T))
                self.shuffled_player_states.append(PlayerState(id, team_num, table_num, seat_num, gossip, color))
            elif team_num == 3:
                self.shuffled_players.append(Player3(id, team_num, table_num, seat_num, gossip, color, self.T))
                self.shuffled_player_states.append(PlayerState(id, team_num, table_num, seat_num, gossip, color))
            elif team_num == 4:
                self.shuffled_players.append(Player4(id, team_num, table_num, seat_num, gossip, color, self.T))
                self.shuffled_player_states.append(PlayerState(id, team_num, table_num, seat_num, gossip, color))
            elif team_num == 5:
                self.shuffled_players.append(Player5(id, team_num, table_num, seat_num, gossip, color, self.T))
                self.shuffled_player_states.append(PlayerState(id, team_num, table_num, seat_num, gossip, color))
            elif team_num == 6:
                self.shuffled_players.append(Player6(id, team_num, table_num, seat_num, gossip, color, self.T))
                self.shuffled_player_states.append(PlayerState(id, team_num, table_num, seat_num, gossip, color))
            elif team_num == 7:
                self.shuffled_players.append(Player7(id, team_num, table_num, seat_num, gossip, color, self.T))
                self.shuffled_player_states.append(PlayerState(id, team_num, table_num, seat_num, gossip, color))
            else:
                self.shuffled_players.append(DefaultPlayer(id, team_num, table_num, seat_num, gossip, color, self.T))
                self.shuffled_player_states.append(PlayerState(id, team_num, table_num, seat_num, gossip, color))

        self.players = sorted(self.shuffled_players, key=lambda x: x.id)
        self.player_states = sorted(self.shuffled_player_states, key=lambda x: x.id)

    def resume(self):
        if self.game_state != "over":
            self.game_state = "resume"
            self.root.after(100, self._play_game)

    def pause(self):
        if self.game_state != "over":
            self.game_state = "pause"

    def step(self):
        if self.game_state != "over":
            self.game_state = "pause"
            self.root.after(100, self._play_game)

    def _update_ui(self):
        self.canvas.itemconfigure(self.turn_comp, text="Turn: " + str(self.turn) + "/" + str(self.T))
        self.canvas.itemconfigure(self.group_score_comp, text="Group Score: " + str(round(self.group_score / 90, 2)))


        for i in range(10):
            for j in range(10):
                self.canvas.itemconfigure(self.table_comps[i][j], start=0, extent=359, fill="#BA9058", outline="#BA9058")
                self.canvas.itemconfigure(self.turn_eyes_comp[i][j], fill="#BA9058", outline="#BA9058")
                self.canvas.itemconfigure(self.left_eyes_comp[i][j], fill="#BA9058", outline="#BA9058")
                self.canvas.itemconfigure(self.right_eyes_comp[i][j], fill="#BA9058", outline="#BA9058")
                self.canvas.itemconfigure(self.seat_label_comps[i][j], text="")
                self.canvas.itemconfigure(self.id_label_comps[i][j], text="")

        for index, player_state in enumerate(self.player_states):
            table = player_state.table_num
            seat = player_state.seat_num
            color = player_state.color
            id = player_state.id
            direction = player_state.direction
            action = player_state.action[0]
            self.canvas.itemconfigure(self.seat_label_comps[table][seat], text="")
            self.canvas.itemconfigure(self.id_label_comps[table][seat], text="")

            if action == 'talk':
                self.canvas.itemconfigure(self.seat_label_comps[table][seat], text=player_state.curr_state)
                self.canvas.itemconfigure(self.id_label_comps[table][seat], text=str(id))

                self.canvas.itemconfigure(self.turn_eyes_comp[table][seat], fill="#000000", outline="#000000")
                self.canvas.itemconfigure(self.left_eyes_comp[table][seat], fill=color, outline=color)
                self.canvas.itemconfigure(self.right_eyes_comp[table][seat], fill=color, outline=color)
                if direction == 'left':
                    self.canvas.itemconfigure(self.table_comps[table][seat], start=self.left_talk_angle[seat][0], extent=self.left_talk_angle[seat][1], fill=color, outline="#000000", width=5, style=tk.PIESLICE)
                else:
                    self.canvas.itemconfigure(self.table_comps[table][seat], start=self.right_talk_angle[seat][0], extent=self.right_talk_angle[seat][1], fill=color, outline="#000000", width=5, style=tk.PIESLICE)
            elif action == 'listen':
                self.canvas.itemconfigure(self.seat_label_comps[table][seat], text=player_state.curr_state)
                self.canvas.itemconfigure(self.id_label_comps[table][seat], text=str(id))
                self.canvas.itemconfigure(self.turn_eyes_comp[table][seat], fill="#000000", outline="#000000")
                self.canvas.itemconfigure(self.left_eyes_comp[table][seat], fill=color, outline=color)
                self.canvas.itemconfigure(self.right_eyes_comp[table][seat], fill=color, outline=color)
                if direction == 'left':
                    self.canvas.itemconfigure(self.table_comps[table][seat], start=self.left_listen_angle[seat][0], extent=self.left_listen_angle[seat][1], fill=color, outline="#000000", width=5, style=tk.PIESLICE)
                else:
                    self.canvas.itemconfigure(self.table_comps[table][seat], start=self.right_listen_angle[seat][0], extent=self.right_listen_angle[seat][1], fill=color, outline="#000000", width=5, style=tk.PIESLICE)
            elif action == 'move':
                self.canvas.itemconfigure(self.id_label_comps[table][seat], text=str(id))
                self.canvas.itemconfigure(self.turn_eyes_comp[table][seat], fill=color, outline=color)
                self.canvas.itemconfigure(self.left_eyes_comp[table][seat], fill="#000000", outline="#000000")
                self.canvas.itemconfigure(self.right_eyes_comp[table][seat], fill="#000000", outline="#000000")
                self.canvas.itemconfigure(self.table_comps[table][seat], start=self.left_listen_angle[seat][0], extent=self.left_listen_angle[seat][1], fill=color, outline="#ffffff", width=5, style="chord")
                    
            for index, player_state in enumerate(self.shuffled_player_states):
                team_num = player_state.team_num
                player_id = player_state.id
                individual_score = player_state.individual_score
                intial_gossip = player_state.initial_gossip
                self.canvas2.itemconfigure(self.canvas2_text_comp[index], text=str(player_id).ljust(6, " ") + str(team_num).ljust(6, " ") + str(individual_score).ljust(18, " ") + str(intial_gossip).ljust(16, " ") + "\n")

    def _render_frame(self):
        frame=tk.Frame(self.root2,width=450,height=2800)
        frame.pack(expand=True, fill=BOTH)
        self.canvas2=tk.Canvas(frame,bg='#FFFFFF',width=600,height=600,scrollregion=(0,0,600,2800))
        hbar=Scrollbar(frame,orient=HORIZONTAL)
        hbar.pack(side=BOTTOM,fill=X)
        hbar.config(command=self.canvas2.xview)
        vbar=Scrollbar(frame,orient=VERTICAL)
        vbar.pack(side=RIGHT,fill=Y)
        vbar.config(command=self.canvas2.yview)
        self.canvas2.config(yscrollcommand=vbar.set)
        self.canvas2.pack(side=LEFT,expand=True,fill=BOTH)

        self.canvas = tk.Canvas(self.root, height=70 * self.scale, width=155 * self.scale, bg="#FCF1E3")
        centers = []
        table = 0

        for j in range(2):
            for i in range(5):
                interval = 30 * self.scale
                x = ((interval* i) + (interval * (i + 1))) / 2
                y = ((interval * j + 8 * self.scale) + (interval * (j + 1) + 8 * self.scale)) / 2
                centers.append([x, y])
                self.canvas.create_oval(interval * i + 8 * self.scale, interval * j + 16 * self.scale, interval * (i + 1) - 8 * self.scale, interval * (j + 1), outline="#683F0B", fill="#9B784B",width=5)
                
                # Load an image in the script
                img= (Image.open("./icons/" + str(table) + ".png"))

                # Resize the Image using resize method
                resized_image= img.resize((14 * self.scale,14 * self.scale), Image.LANCZOS)
                self.icons.append(ImageTk.PhotoImage(resized_image))

                self.canvas.create_image(interval * i + 8 * self.scale, interval * j + 16 * self.scale,anchor=NW,image=self.icons[table])

                seats = []
                seat_labels = []
                id_labels = []
                player_eyes = []
                left_eyes = []
                right_eyes = []
                r1 = 11 * self.scale
                r2 = 12 * self.scale
                r3 = 13 * self.scale
                r4 = 12 * self.scale
                r5 = 9 * self.scale

                for i in range(10):
                    r3 = 13 * self.scale
                    r5 = 7.5 * self.scale
                    degree_angle = 36 * i
                    angle = (degree_angle * math.pi/ 180)
                    l_angle = ((degree_angle - 4) * math.pi/ 180)
                    r_angle = ((degree_angle + 4) * math.pi/ 180)
                    cy = y + r1 * math.cos(angle)
                    cx = x + r1 * math.sin(angle)

                    iy = y + r2 * math.cos(angle)
                    ix = x + r2 * math.sin(angle)

                    ly = y + r4 * math.cos(l_angle)
                    lx = x + r4 * math.sin(l_angle)


                    ry = y + r4 * math.cos(r_angle)
                    rx = x + r4 * math.sin(r_angle)

                    text_angle = degree_angle


                    if text_angle >= 108 and text_angle <= 252:
                        text_angle -= 195
                        r3 += 1.5 * self.scale
                        r5 += 1.5 * self.scale

                    ty = y + r3 * math.cos(angle)
                    tx = x + r3 * math.sin(angle)

                    idy = y + r5 * math.cos(angle)
                    idx = x + r5 * math.sin(angle)

                    seat = self.canvas.create_arc([cx - 1.8 * self.scale, cy - 1.8 * self.scale, cx + 1.8 * self.scale, cy + 1.8 * self.scale], start=0, extent=359, outline="#BA9058", fill="#BA9058", style=tk.PIESLICE)
                    
                    eyes = self.canvas.create_oval(ix - 0.2 * self.scale, iy - 0.2 * self.scale, ix + 0.2 * self.scale, iy + 0.2 * self.scale, outline="#BA9058", fill="#BA9058",width=0.2 * self.scale)
                    left_eye = self.canvas.create_oval(lx - 0.2 * self.scale, ly - 0.2 * self.scale, lx + 0.2 * self.scale, ly + 0.2 * self.scale, outline="#BA9058", fill="#BA9058",width=0.2 * self.scale)
                    right_eye = self.canvas.create_oval(rx - 0.2 * self.scale, ry - 0.2 * self.scale, rx + 0.2 * self.scale, ry + 0.2 * self.scale, outline="#BA9058", fill="#BA9058",width=0.2 * self.scale)
                    
                    label = self.canvas.create_text(tx, ty, anchor="nw", font=('freemono', 11, 'bold'), angle=str(text_angle), text="")
                    id_label = self.canvas.create_text(idx, idy, anchor="nw", font=('Comic Sans MS', 13, 'bold'), angle=str(text_angle), text="")
                    
                    seats.append(seat)
                    seat_labels.append(label)
                    id_labels.append(id_label)
                    player_eyes.append(eyes)
                    left_eyes.append(left_eye)
                    right_eyes.append(right_eye)

                self.table_comps.append(seats)
                self.seat_label_comps.append(seat_labels)
                self.id_label_comps.append(id_labels)
                self.turn_eyes_comp.append(player_eyes)
                self.left_eyes_comp.append(left_eyes)
                self.right_eyes_comp.append(right_eyes)
                table += 1

        for index, player_state in enumerate(self.player_states):
            table = player_state.table_num
            seat = player_state.seat_num
            color = player_state.color
            id = player_state.id
            self.canvas.itemconfigure(self.table_comps[table][seat], start=self.left_listen_angle[seat][0], extent=self.left_listen_angle[seat][1], fill=color, outline="#000000", width=5, style="chord")
            self.canvas.itemconfigure(self.turn_eyes_comp[table][seat], outline=color, fill=color)
            self.canvas.itemconfigure(self.left_eyes_comp[table][seat], outline="#000000", fill="#000000")
            self.canvas.itemconfigure(self.right_eyes_comp[table][seat], outline="#000000", fill="#000000")

        s1 = "ID"
        s2 = "Team"
        s3 = "Individual Score"
        s4 = "Initial Gossip"
        
        self.canvas2.create_text(3 * self.scale, 7 * self.scale, anchor="nw", font=('Helvetica', int(1.8 * self.scale), 'bold'), text=s1.ljust(6, " ") + s2.ljust(6, " ") + s3.ljust(18, " ") + s4.ljust(16, " ") + "\n")

        for index, player_state in enumerate(self.shuffled_player_states):
            team_num = player_state.team_num
            player_id = player_state.id
            individual_score = player_state.individual_score
            inital_gossip = player_state.initial_gossip
            text_comp = self.canvas2.create_text(3 * self.scale, 3 * self.scale * index + 10 * self.scale, anchor="nw", font=('Helvetica', int(1.8 * self.scale), 'bold'), text=str(player_id).ljust(6, " ") + str(team_num).ljust(6, " ") + str(individual_score).ljust(18, " ") + str(inital_gossip).ljust(16, " ") + "\n")
            self.canvas2.create_oval(1 * self.scale, 3 * self.scale * index + 10 * self.scale, int(2.2 * self.scale), int(3 * self.scale * index + 11.2 * self.scale), fill=player_state.color)
            self.canvas2_text_comp.append(text_comp)
        
        self.turn_comp = self.canvas.create_text(30 * self.scale, 3.5 * self.scale, anchor="nw", font=('Helvetica', int(1.8 * self.scale), 'bold'), text="Turn: " + str(self.turn) + "/" + str(self.T))
        self.group_score_comp = self.canvas.create_text(100 * self.scale, 3.5 * self.scale, anchor="nw", font=('Helvetica', int(1.8 * self.scale), 'bold'), text="Group Score: " + str(round(self.group_score / 90, 2)))

        pause_btn = Button(self.canvas, width=int(0.8 * self.scale), height=int(0.2 * self.scale), bd='10', command=self.pause, font=('freemono', int(1.3 * self.scale), 'bold'), text="PAUSE", bg="#E3AB62")
        pause_btn.place(x=60 * self.scale, y=1 * self.scale)

        resume_btn = Button(self.canvas, width=int(0.8 * self.scale), height=int(0.2 * self.scale), bd='10', command=self.resume, font=('freemono', int(1.3 * self.scale), 'bold'), text="START/\nRESUME", bg="#E3AB62")
        resume_btn.place(x=70 * self.scale, y=1 * self.scale)

        step_btn = Button(self.canvas, width=int(0.8 * self.scale), height=int(0.2 * self.scale), bd='10', command=self.step, font=('freemono', int(1.3 * self.scale), 'bold'), text="STEP", bg="#E3AB62")
        step_btn.place(x=80 * self.scale, y=1 * self.scale)

        self.canvas.pack()

    def move_player(self, index, player, priority_list):
        empty_seat_list = []
        for table_num in range(10):
            for seat_num in range(10):
                seat = self.tables[table_num].seats[seat_num]
                if seat == [-1, -1]:
                    empty_seat_list.append([table_num, seat_num])

        curr_table_num = self.player_states[index].table_num
        curr_seat_num = self.player_states[index].seat_num

        id = self.player_states[index].id
        team_num = self.player_states[index].team_num

        if len(priority_list) > 10:
            return 0

        for moves in priority_list:
            table_num, seat_num = moves[0], moves[1]

            if [table_num, seat_num] in empty_seat_list:
                # check if new position is occupied
                if self.tables[table_num].seats[seat_num] == [-1, -1]:
                    # move player from old position to new position
                    self.tables[curr_table_num].seats[curr_seat_num] = [-1, -1]
                    self.tables[table_num].seats[seat_num] = [id, team_num]

                    # update player
                    player.table_num = table_num
                    player.seat_num = seat_num

                    # update player state
                    self.player_states[index].table_num = table_num
                    self.player_states[index].seat_num = seat_num

                    self.attendee_logs[index] += " Moved to Table Num: " + str(table_num) + " Seat Num: " + str(seat_num)
                    return 1
        return 0

    # observe before turn
    def get_player_positions(self):
        player_positions = []
        for player_state in self.player_states:
            player_id = player_state.id
            table_num = player_state.table_num
            seat_num = player_state.seat_num
            player_positions.append([player_id, table_num, seat_num])

        return player_positions
    
    def get_player_recent_actions(self, player_id):
        player_actions = []
        table_num = self.player_states[player_id].table_num
        for player_state in self.player_states:
            if player_state.table_num == table_num:
                if player_state.action[0] == 'talk':
                    action = [player_state.id, [player_state.action[0], player_state.action[1]]]
                    player_actions.append(action)
                elif player_state.action[0] == 'listen':
                    action = [player_state.id, [player_state.action[0], player_state.action[1]]]
                    player_actions.append(action)

        return player_actions

    def _play_game(self):
        self.attendee_logs = []
        scores = {}
        avg_scores = {}
        if self.turn > self.T:
            self.game_state = "over"
            with open(self.result, 'a') as f:
                f.write("Results\n")
                f.write("Group Score: " + str(round(self.group_score / 90, 2)) + "\n")

            for index, player_state in enumerate(self.player_states):
                team_num = player_state.team_num
                if team_num in scores.keys():
                    scores[team_num].append(player_state.individual_score)
                else:
                    scores[team_num] = [player_state.individual_score]

            with open(self.result, 'a') as f:
                f.write("\n\n\nAverage Team Scores\n")

            for team in sorted(scores.keys()):
                print(team)
                total = 0
                total_score = 0
                for score in scores[team]:
                    total_score += score
                    total += 1

                avg_scores[team] = round(total_score / total, 2)

            sorted_avg_scores = sorted(avg_scores.items(), key=lambda x:x[1])[::-1]
            for team, score in sorted_avg_scores:
                with open(self.result, 'a') as f:
                    f.write("Team " + str(team) + ": " + str(score) + "\n")

            with open(self.result, 'a') as f:
                f.write("\n\n\nAttendee Scores\n")
            for index, player_state in enumerate(self.player_states):
                with open(self.result, 'a') as f:
                    f.write("Attendee: " + str(player_state.id) + " Team: " + str(player_state.team_num) + " Individual Score: " + str(player_state.individual_score) + " Initial Gossip: " + str(player_state.initial_gossip) + "\n")


        if self.game_state != "over":
            action_list = []
            feedback = [[] for _ in range(len(self.player_states))]
            move_players = []
            self.check_move = [0] * 90

            player_positions = self.get_player_positions()

            with open(self.log, 'a') as f:
                f.write("Turn: " + str(self.turn) + "\n")

            for index, player in enumerate(self.players):
                # get action
                self.player_states[index].curr_state = ""
                start_time = time.time()
                player.observe_before_turn(player_positions)
                action = player.get_action()
                end_time = time.time()
                self.attendee_logs.append("Attendee: " + str(index) + " Team: " + str(self.player_states[index].team_num) + \
                                          " Current Table Num: " + str(self.player_states[index].table_num) + \
                                          " Current Seat Num: " + str(self.player_states[index].seat_num) + \
                                          " Action: " + str(action) + "Time Taken: " + str(end_time - start_time))
                action_type = action[0]
                if action_type == 'talk':
                    direction = action[1]
                    gossip = action[2]
                    self.player_states[index].curr_state = str(gossip)
                    self.player_states[index].direction = direction

                    # check if gossip to share is present in the player's gossip list
                    if gossip not in self.player_states[index].gossip_list:
                        action_list.append(["invalid action"])
                    else:
                        action_list.append(action)
                        self.player_states[index].action = action

                elif action_type == 'move':
                    priority_list = action[1]
                    move_players.append([index, priority_list])
                    action_list.append(action)
                    self.player_states[index].action = action
                elif action_type == 'listen':
                    action_list.append(action)
                    self.player_states[index].action = action
                else:
                    action_list.append(["invalid action"])
                
            for index, action in enumerate(action_list):
                action_type = action[0]
                if action_type == 'listen':
                    direction = action[1]

                    if direction == 'left':
                        self.player_states[index].direction = direction
                        table_num = self.player_states[index].table_num
                        seat_num = self.player_states[index].seat_num

                        table = self.tables[table_num]
                        seats = table.seats

                        left_positions = [(seat_num - 1) % 10, (seat_num - 2) % 10, (seat_num - 3) % 10]
                        left_player_ids = []
                        left_player_actions = []
                        for pos in left_positions:
                            lp_id = seats[pos][0]
                            if lp_id != -1:
                                if action_list[lp_id][0] == 'talk':
                                    if action_list[lp_id][1] == 'right':
                                        left_player_ids.append(lp_id)
                                        left_player_actions.append(action_list[lp_id])
                        
                        # highest gossip value
                        highest_gossip_val = -1
                        highest_gossip_talker = -1

                        # highest gossip value that is new to the listening player
                        new_gossip_val = -1
                        new_gossip_talker = -1

                        for lp_index, lp_action in enumerate(left_player_actions):
                            if lp_action[0] == 'talk':
                                talking_direction = lp_action[1]
                                gossip_item = int(lp_action[2])
                                if gossip_item > highest_gossip_val:
                                    highest_gossip_val = gossip_item
                                    highest_gossip_talker = left_player_ids[lp_index]

                                if gossip_item not in self.player_states[index].gossip_list and gossip_item > new_gossip_val:
                                    new_gossip_val = gossip_item
                                    new_gossip_talker = left_player_ids[lp_index]

                        if new_gossip_val == -1:
                            # all gossip items from the talking players are not new to the listening player or
                            # there were no talking players on the left or
                            # players on the left were talking in the opposite direction
                            # check is any player was talking in the left direction, if so find the player 
                            # conveying the gossip item with the highest value'
                            if highest_gossip_val == -1:
                                # no player on the left was talking towards the right
                                # no feedback is returned
                                self.attendee_logs[index] += " Listened Nothing"
                                pass
                            else:
                                # feedback is sent to the talker who has the highest gossip value
                                feedback[highest_gossip_talker].append("Shake Head " + str(index))
                                self.player_states[index].curr_state = "S"
                                self.attendee_logs[index] += " Shaked Head to Attendee " + str(highest_gossip_talker) + " from Team " + str(self.player_states[highest_gossip_talker].team_num)
                                
                        else:
                            feedback[new_gossip_talker].append("Nod Head " + str(index))
                            self.player_states[index].curr_state = "N," + str(new_gossip_talker)
                            self.player_states[new_gossip_talker].individual_score += new_gossip_val
                            self.group_score += new_gossip_val
                            self.player_states[index].gossip_list.append(new_gossip_val)
                            self.players[index].get_gossip(new_gossip_val, new_gossip_talker)
                            self.attendee_logs[index] += " Nod Head to Attendee " + str(new_gossip_talker) + " from Team " + str(self.player_states[new_gossip_talker].team_num)

                    elif direction == 'right':
                        self.player_states[index].direction = direction
                        table_num = self.player_states[index].table_num
                        seat_num = self.player_states[index].seat_num

                        table = self.tables[table_num]
                        seats = table.seats

                        right_positions = [(seat_num + 1) % 10, (seat_num + 2) % 10, (seat_num + 3) % 10]
                        right_player_ids = []
                        right_player_actions = []
                        for pos in right_positions:
                            rp_id = seats[pos][0]
                            if rp_id != -1:
                                if action_list[rp_id][0] == 'talk':
                                    if action_list[rp_id][1] == 'left':
                                        right_player_ids.append(rp_id)
                                        right_player_actions.append(action_list[rp_id])
                        
                        # highest gossip value
                        highest_gossip_val = -1
                        highest_gossip_talker = -1

                        # highest gossip value that is new to the listening player
                        new_gossip_val = -1
                        new_gossip_talker = -1

                        for rp_index, rp_action in enumerate(right_player_actions):
                            if rp_action[0] == 'talk':
                                talking_direction = rp_action[1]
                                gossip_item = int(rp_action[2])
                                if talking_direction == 'left':
                                    if gossip_item > highest_gossip_val:
                                        highest_gossip_val = gossip_item
                                        highest_gossip_talker = right_player_ids[rp_index]

                                    if gossip_item not in self.player_states[index].gossip_list and gossip_item > new_gossip_val:
                                        new_gossip_val = gossip_item
                                        new_gossip_talker = right_player_ids[rp_index]

                        if new_gossip_val == -1:
                            # all gossip items from the talking players are not new to the listening player or
                            # there were no talking players on the left or
                            # players on the left were talking in the opposite direction
                            # check is any player was talking in the left direction, if so find the player 
                            # conveying the gossip item with the highest value'
                            if highest_gossip_val == -1:
                                # no player on the left was talking towards the right
                                # no feedback is returned
                                self.attendee_logs[index] += " Listened Nothing"
                                pass
                            else:
                                # feedback is sent to the talker who has the highest gossip value
                                feedback[highest_gossip_talker].append("Shake Head " + str(index))
                                self.player_states[highest_gossip_talker].curr_state = "S"
                                self.attendee_logs[index] += " Shaked Head to Attendee " + str(highest_gossip_talker) + " from Team " + str(self.player_states[highest_gossip_talker].team_num)
                        else:
                            feedback[new_gossip_talker].append("Nod Head " + str(index))
                            self.player_states[index].curr_state = "N," + str(new_gossip_talker)
                            self.player_states[new_gossip_talker].individual_score += new_gossip_val
                            self.group_score += new_gossip_val
                            self.player_states[index].gossip_list.append(new_gossip_val)
                            self.players[index].get_gossip(new_gossip_val, new_gossip_talker)
                            self.attendee_logs[index] += " Nod Head to Attendee " + str(new_gossip_talker) + " from Team " + str(self.player_states[new_gossip_talker].team_num)
                
                elif action_type == 'move':
                    random.shuffle(move_players)

                    for move in move_players:
                        player_id = move[0]
                        priority_list = move[1]
                        player = self.players[player_id]
                        self.check_move[player_id] = self.move_player(player_id, player, priority_list)
            
            for index, action in enumerate(action_list):
                action_type = action[0]
                if action_type == 'talk':
                    self.players[index].feedback(feedback[index])
                    self.attendee_logs[index] += "Received Feedback: " + str(feedback[index])

            for index, action in enumerate(action_list):
                player_actions = self.get_player_recent_actions(index)
                self.players[index].observe_after_turn(player_actions)

            for log in self.attendee_logs:
                with open(self.log, 'a') as f:
                    f.write(log + "\n")

            if self.gui:
                self._update_ui()
            
            self.turn += 1

            if self.game_state == "resume":
                if self.gui:
                    self.root.after(self.interval, self._play_game)
                else:
                    self._play_game()
