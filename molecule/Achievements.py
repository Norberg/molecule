
class Achievement:
    def __init__(self, key, name, description, thresholds):
        self.key = key
        self.name = name
        self.description = description
        self.thresholds = thresholds  # dict: {"bronze": val, "silver": val, "gold": val}

    def check(self, current_value, unlocked_levels):
        new_unlocks = []
        for level, threshold in self.thresholds.items():
            if current_value >= threshold and level not in unlocked_levels:
                new_unlocks.append(level)
        return new_unlocks

class AchievementManager:
    def __init__(self):
        self.achievements = [
            Achievement("molecule_discover", "Molecule Discover", "Find unique molecules", 
                        {"bronze": 15, "silver": 30, "gold": 50}),
            Achievement("reaction_discover", "Reaction Discover", "Find unique reactions", 
                        {"bronze": 15, "silver": 30, "gold": 50}),
            Achievement("reactionist", "Reactionist", "Perform reactions", 
                        {"bronze": 100, "silver": 200, "gold": 500}),
            Achievement("molecule_maker", "Molecule Maker", "Create molecules", 
                        {"bronze": 200, "silver": 500, "gold": 1000}),
            Achievement("level_crusher", "Level Crusher", "Solve levels", 
                        {"bronze": 10, "silver": 20, "gold": 50}),
        ]

    def get_player_stats(self, player_id, persistence):
        if player_id is None:
            return {}

        # 1. Molecule Discover (Unique viewed molecules)
        seen_molecules = persistence.get_seen_molecules(player_id)
        count_seen = len(seen_molecules)

        # 2. Reaction Discover (Unique performed reactions)
        performed_reactions = persistence.get_performed_reactions(player_id)
        count_unique_reactions = len(performed_reactions)

        # 3. Reactionist (Total reactions performed)
        count_total_reactions = sum(r["total_count"] for r in performed_reactions)
        
        # 4. Molecule Maker (Total molecules created)
        created_molecules = persistence.get_created_molecules(player_id)
        count_total_created = sum(created_molecules.values())

        # 5. Level Crusher (Levels solved)
        completed_levels = persistence.get_completed_levels(player_id)
        count_levels = len(completed_levels)

        # Map stats to achievement keys
        return {
            "molecule_discover": count_seen,
            "reaction_discover": count_unique_reactions,
            "reactionist": count_total_reactions,
            "molecule_maker": count_total_created,
            "level_crusher": count_levels
        }

    def check_and_unlock(self, player_id, persistence):
        if player_id is None:
            return []

        stats = self.get_player_stats(player_id, persistence)

        # Get existing achievements
        existing = persistence.get_player_achievements(player_id)
        # existing is list of dicts: {'key': '...', 'level': '...', ...}
        
        # Organize existing check
        unlocked_map = {} # key -> set of levels
        for entry in existing:
            if entry["key"] not in unlocked_map:
                unlocked_map[entry["key"]] = set()
            unlocked_map[entry["key"]].add(entry["level"])

        newly_unlocked = []

        for ach in self.achievements:
            current_val = stats.get(ach.key, 0)
            already_unlocked = unlocked_map.get(ach.key, set())
            
            new_levels = ach.check(current_val, already_unlocked)
            for level in new_levels:
                persistence.unlock_achievement(player_id, ach.key, level)
                newly_unlocked.append({
                    "key": ach.key,
                    "name": ach.name,
                    "level": level,
                    "description": ach.description
                })
        
        return newly_unlocked
