package com.century.sport.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/**
 * Represents a complete game level with questions
 */
@Serializable
data class Level(
    val id: Int,
    val title: String,
    val difficulty: String,
    val questions: List<Question>
)

/**
 * Represents a single question in the quiz
 */
@Serializable
data class Question(
    val id: Int,
    val text: String,
    @SerialName("correctAnswer")
    val correctAnswer: String,
    @SerialName("wrongAnswers")
    val wrongAnswers: List<String>,
    val year: Int? = null,
    val imageUrl: String? = null
) {
    /**
     * Returns all answer options (correct + wrong) in a randomized order
     */
    fun getAllOptions(): List<String> {
        val allOptions = wrongAnswers.toMutableList()
        allOptions.add(correctAnswer)
        return allOptions.shuffled()
    }
    
    /**
     * Checks if the given answer is correct
     */
    fun isCorrectAnswer(answer: String): Boolean {
        return answer == correctAnswer
    }
}

/**
 * Represents a player's progress in a specific level
 */
@Serializable
data class LevelProgress(
    val levelId: Int,
    val correctAnswers: Int = 0,
    val wrongAnswers: Int = 0,
    val completed: Boolean = false,
    val lastPlayedTimestamp: Long = 0
)

/**
 * Represents the overall player stats across all levels
 */
@Serializable
data class PlayerStats(
    val totalCorrectAnswers: Int = 0,
    val totalWrongAnswers: Int = 0,
    val levelsCompleted: Int = 0
) 