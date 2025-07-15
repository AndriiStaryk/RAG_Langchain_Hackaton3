package com.century.sport.viewmodel

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.century.sport.data.StorageHelper
import com.century.sport.model.Level
import com.century.sport.model.LevelModel
import com.century.sport.model.LevelProgress
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class LevelViewModel(
    private val storageHelper: StorageHelper,
    private val sportOrder: Int
) : ViewModel() {
    
    // UI state
    private val _uiState = MutableStateFlow<LevelsUiState>(LevelsUiState.Loading)
    val uiState: StateFlow<LevelsUiState> = _uiState
    
    // Level data with state information
    private val _levelStates = MutableStateFlow<List<LevelWithState>>(emptyList())
    val levelStates: StateFlow<List<LevelWithState>> = _levelStates
    
    init {
        loadLevels()
    }
    
    /**
     * Refreshes the level data
     */
    fun refreshLevels() {
        Log.d("LevelViewModel", "Refreshing levels data")
        loadLevels()
    }
    
    private fun loadLevels() {
        viewModelScope.launch {
            try {
                // Get the levels for this sport
                val AF = "american_football.json"
                val B = "basketball.json"
                val F = "football.json"
                val GOLF_LEVELS_ASSET = "golf.json"
                val T = "tennis.json"
                val sport = when (sportOrder){
                    0 -> AF
                    1 -> B
                    2 -> F
                    3 -> GOLF_LEVELS_ASSET
                    4 -> T
                    else -> {AF}
                }

                val levels = storageHelper.getLevelsForSport(sport)
                
                // Get the user's progress for all levels
                val allProgress = storageHelper.getAllLevelProgress()
                Log.d("LevelViewModel", "Loaded progress: $allProgress")
                
                // Determine the state of each level
                val levelsWithState = determineLevelStates(levels, allProgress)
                
                _levelStates.value = levelsWithState
                _uiState.value = LevelsUiState.Success(levelsWithState)
            } catch (e: Exception) {
                _uiState.value = LevelsUiState.Error("Failed to load levels: ${e.message}")
            }
        }
    }
    
    private fun determineLevelStates(
        levels: List<Level>,
        progress: List<LevelProgress>
    ): List<LevelWithState> {
        val result = mutableListOf<LevelWithState>()
        
        Log.d("LevelViewModel", "Determining states for ${levels.size} levels with ${progress.size} progress entries")
        Log.d("LevelViewModel", "Progress entries: $progress")
        
        // First level is always unlocked
        var previousLevelPassed = true
        
        for (level in levels) {
            // Find progress for this level
            val levelProgress = progress.find { it.levelId == level.id }
            
            // Determine state
            val state = when {
                levelProgress?.completed == true -> LevelState.PASSED
                previousLevelPassed -> LevelState.UNLOCKED
                else -> LevelState.LOCKED
            }
            
            Log.d("LevelViewModel", "Level ${level.id} (${level.title}): progress=$levelProgress, state=$state")
            
            result.add(LevelWithState(level, state, levelProgress))
            
            // Update for next iteration
            previousLevelPassed = state == LevelState.PASSED
        }
        
        return result
    }
    
    /**
     * Factory for creating the ViewModel with parameters
     */
    class Factory(
        private val storageHelper: StorageHelper,
        private val sportOrder: Int
    ) : ViewModelProvider.Factory {
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            if (modelClass.isAssignableFrom(LevelViewModel::class.java)) {
                @Suppress("UNCHECKED_CAST")
                return LevelViewModel(storageHelper, sportOrder) as T
            }
            throw IllegalArgumentException("Unknown ViewModel class")
        }
    }
}

/**
 * Represents the UI state of the levels screen
 */
sealed class LevelsUiState {
    object Loading : LevelsUiState()
    data class Success(val levels: List<LevelWithState>) : LevelsUiState()
    data class Error(val message: String) : LevelsUiState()
}

/**
 * Represents a level with its current state
 */
data class LevelWithState(
    val level: Level,
    val state: LevelState,
    val progress: LevelProgress? = null
)

/**
 * Possible states for a level
 */
enum class LevelState {
    PASSED,
    UNLOCKED,
    LOCKED
} 