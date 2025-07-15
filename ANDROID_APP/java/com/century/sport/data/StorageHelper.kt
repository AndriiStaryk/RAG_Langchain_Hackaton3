package com.century.sport.data

import android.content.Context
import android.content.SharedPreferences
import android.util.Log
import com.century.sport.model.*
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import java.io.IOException

/**
 * Helper class for managing data storage and retrieval
 */
class StorageHelper(private val context: Context) {

    companion object {
        // Constants for asset files
        const val AF = "american_football.json"
        const val B = "basketball.json"
        const val F = "football.json"
        const val GOLF_LEVELS_ASSET = "golf.json"
        const val T = "tennis.json"

        // SharedPreferences keys
        private const val PREFS_NAME = "SportQuizPrefs"
        private const val KEY_PLAYER_STATS = "player_stats"
        private const val KEY_LEVEL_PROGRESS_PREFIX = "level_progress_"

        // JSON parser configuration
        private val json = Json {
            ignoreUnknownKeys = true
            isLenient = true
        }
    }

    private val sharedPreferences: SharedPreferences by lazy {
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    }

    /**
     * Loads a level from the specified asset file
     */
    fun loadLevelFromAsset(assetPath: String): List<Level>? {
        return try {
            val jsonString = context.assets.open(assetPath).bufferedReader().use { it.readText() }
            val decoded: List<Level> = json.decodeFromString(jsonString)
            println("decoded")
            decoded
        } catch (e: Exception) {
            Log.e("StorageHelper", "Error loading level from asset: $assetPath", e)
            null
        }
    }

    /**
     * Saves the player's answer for a specific question
     */
    fun saveAnswer(levelId: Int, isCorrect: Boolean) {
        val levelProgress = getLevelProgress(levelId)

        val updatedProgress = if (isCorrect) {
            levelProgress.copy(
                correctAnswers = levelProgress.correctAnswers + 1,
                lastPlayedTimestamp = System.currentTimeMillis()
            )
        } else {
            levelProgress.copy(
                wrongAnswers = levelProgress.wrongAnswers + 1,
                lastPlayedTimestamp = System.currentTimeMillis()
            )
        }

        saveLevelProgress(updatedProgress)
        updatePlayerStats(isCorrect)
    }

    /**
     * Marks a level as completed
     */
    fun markLevelCompleted(levelId: Int) {
        val progress = getLevelProgress(levelId)
        
        Log.d("StorageHelper", "Before update - Level $levelId progress: $progress")
        
        // Update the progress to mark it as completed
        val updatedProgress = progress.copy(
            completed = true,
            lastPlayedTimestamp = System.currentTimeMillis()
        )
        
        // Save the updated progress
        saveLevelProgress(updatedProgress)
        
        // Verify the save by retrieving it again
        val verifiedProgress = getLevelProgress(levelId)
        Log.d("StorageHelper", "After update - Level $levelId progress: $verifiedProgress")
    }

    /**
     * Gets the progress for a specific level
     */
    fun getLevelProgress(levelId: Int): LevelProgress {
        val key = KEY_LEVEL_PROGRESS_PREFIX + levelId
        val progressJson = sharedPreferences.getString(key, null)
        
        Log.d("StorageHelper", "Getting progress for level $levelId, key=$key, json=$progressJson")
        
        return if (progressJson != null) {
            try {
                val progress = json.decodeFromString<LevelProgress>(progressJson)
                Log.d("StorageHelper", "Parsed level progress: $progress")
                progress
            } catch (e: Exception) {
                Log.e("StorageHelper", "Error parsing level progress for level $levelId", e)
                LevelProgress(levelId)
            }
        } else {
            Log.d("StorageHelper", "No existing progress found for level $levelId, creating new")
            LevelProgress(levelId)
        }
    }

    /**
     * Gets all level progress data
     */
    fun getAllLevelProgress(): List<LevelProgress> {
        val result = sharedPreferences.all.keys
            .filter { it.startsWith(KEY_LEVEL_PROGRESS_PREFIX) }
            .mapNotNull { key ->
                val progressJson = sharedPreferences.getString(key, null)
                try {
                    progressJson?.let { json.decodeFromString<LevelProgress>(it) }
                } catch (e: Exception) {
                    Log.e("StorageHelper", "Error parsing level progress for key: $key", e)
                    null
                }
            }
        
        Log.d("StorageHelper", "Retrieved ${result.size} level progress entries: $result")
        return result
    }

    /**
     * Gets the player's overall stats
     */
    fun getPlayerStats(): PlayerStats {
        val statsJson = sharedPreferences.getString(KEY_PLAYER_STATS, null)

        return if (statsJson != null) {
            try {
                json.decodeFromString(statsJson)
            } catch (e: Exception) {
                Log.e("StorageHelper", "Error parsing player stats", e)
                PlayerStats()
            }
        } else {
            PlayerStats()
        }
    }

    /**
     * Resets all progress data
     */
    fun resetAllProgress() {
        sharedPreferences.edit().clear().apply()
    }

    /**
     * Resets progress for a specific level
     */
    fun resetLevelProgress(levelId: Int) {
        val key = KEY_LEVEL_PROGRESS_PREFIX + levelId
        sharedPreferences.edit().remove(key).apply()
    }

    /**
     * Updates the player's overall stats
     */
    private fun updatePlayerStats(isCorrect: Boolean) {
        val stats = getPlayerStats()

        val updatedStats = if (isCorrect) {
            stats.copy(totalCorrectAnswers = stats.totalCorrectAnswers + 1)
        } else {
            stats.copy(totalWrongAnswers = stats.totalWrongAnswers + 1)
        }

        savePlayerStats(updatedStats)
    }

    /**
     * Saves the player's level progress
     */
    private fun saveLevelProgress(progress: LevelProgress) {
        // Get existing progress for this specific level
        val key = KEY_LEVEL_PROGRESS_PREFIX + progress.levelId
        
        // Save the progress for this specific level
        val progressJson = Json.encodeToString(LevelProgress.serializer(), progress)
        
        Log.d("StorageHelper", "Saving progress for level ${progress.levelId}, key=$key, json=$progressJson")
        
        val editor = sharedPreferences.edit()
        editor.putString(key, progressJson)
        val success = editor.commit() // Use commit() instead of apply() to get immediate feedback
        
        Log.d("StorageHelper", "Save result for level ${progress.levelId}: $success")
    }

    /**
     * Saves the player's overall stats
     */
    private fun savePlayerStats(stats: PlayerStats) {
        val statsJson = json.encodeToString(stats)
        sharedPreferences.edit().putString(KEY_PLAYER_STATS, statsJson).apply()
    }

    /**
     * Gets levels for a specific sport
     */
    fun getLevelsForSport(sportType: String): List<Level> {
        // In a real app, this would load from a database or API
        // For now, we'll create some dummy levels
        val levels = loadLevelFromAsset(sportType)!!
        Log.d("hi", "levels loaded")
        Log.d("GamesActivity", levels.toString())
        return levels
    }

    /**
     * Debug method to dump all SharedPreferences content
     */
    fun dumpAllPreferences() {
        Log.d("StorageHelper", "=== DUMPING ALL PREFERENCES ===")
        
        val allPrefs = sharedPreferences.all
        Log.d("StorageHelper", "Total entries: ${allPrefs.size}")
        
        allPrefs.forEach { (key, value) ->
            Log.d("StorageHelper", "Key: $key, Value: $value")
        }
        
        Log.d("StorageHelper", "=== END OF PREFERENCES DUMP ===")
    }
} 