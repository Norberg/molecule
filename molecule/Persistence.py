# Molecule - a chemical reaction puzzle game
# Copyright (C) 2013-2026 Simon Norberg <simon@pthread.se>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import sqlite3
import datetime
import os

class Persistence:
    def __init__(self, db_path="progress.db"):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS level_progress (
                    player_id INTEGER,
                    level_path TEXT,
                    first_solved_at DATETIME,
                    first_solved_score FLOAT,
                    PRIMARY KEY (player_id, level_path),
                    FOREIGN KEY (player_id) REFERENCES players(id)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS solved_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER,
                    level_path TEXT,
                    solved_at DATETIME,
                    score FLOAT,
                    FOREIGN KEY (player_id) REFERENCES players(id)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS player_reactions (
                    player_id INTEGER,
                    reaction_title TEXT,
                    first_performed_at DATETIME,
                    total_count INTEGER DEFAULT 0,
                    PRIMARY KEY (player_id, reaction_title),
                    FOREIGN KEY (player_id) REFERENCES players(id)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS player_molecules_seen (
                    player_id INTEGER,
                    molecule_formula TEXT,
                    first_seen_at DATETIME,
                    PRIMARY KEY (player_id, molecule_formula),
                    FOREIGN KEY (player_id) REFERENCES players(id)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS player_molecules_created (
                    player_id INTEGER,
                    molecule_formula TEXT,
                    first_created_at DATETIME,
                    total_count INTEGER DEFAULT 0,
                    PRIMARY KEY (player_id, molecule_formula),
                    FOREIGN KEY (player_id) REFERENCES players(id)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS player_achievements (
                    player_id INTEGER,
                    achievement_key TEXT,
                    level TEXT,
                    unlocked_at DATETIME,
                    PRIMARY KEY (player_id, achievement_key, level),
                    FOREIGN KEY (player_id) REFERENCES players(id)
                )
            """)

            conn.commit()

    def get_player_id(self, name):
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM players WHERE name = ?", (name,))
            row = cur.fetchone()
            if row:
                return row[0]
        return None

    def create_player(self, name):
        with self._get_conn() as conn:
            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO players (name) VALUES (?)", (name,))
                player_id = cur.lastrowid
                conn.commit()
            except sqlite3.IntegrityError:
                player_id = self.get_player_id(name)
        return player_id

    def get_players(self):
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM players")
            return [row[0] for row in cur.fetchall()]

    def mark_completed(self, player_id, level_path, score):
        now = datetime.datetime.now().isoformat()
        with self._get_conn() as conn:
            cur = conn.cursor()
            
            # Check if first time
            cur.execute("SELECT 1 FROM level_progress WHERE player_id = ? AND level_path = ?", (player_id, level_path))
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO level_progress (player_id, level_path, first_solved_at, first_solved_score)
                    VALUES (?, ?, ?, ?)
                """, (player_id, level_path, now, score))
            
            # Add to history
            cur.execute("""
                INSERT INTO solved_history (player_id, level_path, solved_at, score)
                VALUES (?, ?, ?, ?)
            """, (player_id, level_path, now, score))
            
            conn.commit()

    def update_player_stats(self, player_id, reactions, molecules_seen, molecules_created):
        """
        reactions: dict of {reaction_title: count}
        molecules_seen: set of molecule_formula
        molecules_created: dict of {molecule_formula: count}
        """
        now = datetime.datetime.now().isoformat()
        with self._get_conn() as conn:
            cur = conn.cursor()

            # Update reactions
            for title, count in reactions.items():
                cur.execute("""
                    INSERT INTO player_reactions (player_id, reaction_title, first_performed_at, total_count)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(player_id, reaction_title) DO UPDATE SET
                    total_count = total_count + excluded.total_count
                """, (player_id, title, now, count))

            # Update molecules seen
            for formula in molecules_seen:
                cur.execute("""
                    INSERT OR IGNORE INTO player_molecules_seen (player_id, molecule_formula, first_seen_at)
                    VALUES (?, ?, ?)
                """, (player_id, formula, now))

            # Update molecules created
            for formula, count in molecules_created.items():
                cur.execute("""
                    INSERT INTO player_molecules_created (player_id, molecule_formula, first_created_at, total_count)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(player_id, molecule_formula) DO UPDATE SET
                    total_count = total_count + excluded.total_count
                """, (player_id, formula, now, count))

            conn.commit()

    def get_completed_levels(self, player_id):
        if player_id is None:
            return set()
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT level_path FROM level_progress WHERE player_id = ?", (player_id,))
            return set(row[0] for row in cur.fetchall())

    def get_top_scores(self, player_id, level_path, limit=10):
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT solved_at, score FROM solved_history
                WHERE player_id = ? AND level_path = ?
                ORDER BY score ASC, solved_at ASC
                LIMIT ?
            """, (player_id, level_path, limit))
            return cur.fetchall()

    def get_seen_molecules(self, player_id):
        if player_id is None:
            return set()
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT molecule_formula FROM player_molecules_seen WHERE player_id = ?", (player_id,))
            return set(row[0] for row in cur.fetchall())

    def get_created_molecules(self, player_id):
        if player_id is None:
            return {}
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT molecule_formula, total_count FROM player_molecules_created WHERE player_id = ?", (player_id,))
            return {row[0]: row[1] for row in cur.fetchall()}

    def get_performed_reactions(self, player_id):
        if player_id is None:
            return []
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT reaction_title, total_count FROM player_reactions WHERE player_id = ?", (player_id,))
            return [{"reaction_title": row[0], "total_count": row[1]} for row in cur.fetchall()]

    def unlock_achievement(self, player_id, key, level):
        now = datetime.datetime.now().isoformat()
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR IGNORE INTO player_achievements (player_id, achievement_key, level, unlocked_at)
                VALUES (?, ?, ?, ?)
            """, (player_id, key, level, now))
            conn.commit()

    def get_player_achievements(self, player_id):
        if player_id is None:
            return []
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT achievement_key, level, unlocked_at FROM player_achievements WHERE player_id = ?", (player_id,))
            return [{"key": row[0], "level": row[1], "unlocked_at": row[2]} for row in cur.fetchall()]


