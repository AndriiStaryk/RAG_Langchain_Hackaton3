package com.century.sport.viewmodel

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.century.sport.data.StorageHelper
import com.century.sport.model.Level
import com.century.sport.model.Question
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

class QuizViewModel(
    private val storageHelper: StorageHelper,
    private val level: Level
) : ViewModel() {

    // Quiz state
    private val _currentQuestion = MutableStateFlow<Question?>(null)
    val currentQuestion: StateFlow<Question?> = _currentQuestion
    
    private val _questionIndex = MutableStateFlow(0)
    val questionIndex: StateFlow<Int> = _questionIndex
    
    private val _score = MutableStateFlow(0)
    val score: StateFlow<Int> = _score
    
    private val _totalQuestions = MutableStateFlow(0)
    val totalQuestions: StateFlow<Int> = _totalQuestions
    
    private val _answerResult = MutableStateFlow<AnswerResult?>(null)
    val answerResult: StateFlow<AnswerResult?> = _answerResult
    
    private val _isCompleted = MutableStateFlow(false)
    val isCompleted: StateFlow<Boolean> = _isCompleted
    
    // Flag to track if this is the first question load
    private var isFirstQuestion = true
    
    // Initialize the quiz
    init {
        _totalQuestions.value = level.questions.size
        getNextQuestion()
    }
    
    /**
     * Gets the next question in the quiz
     * @return true if there's a next question, false if the quiz is complete
     */
    fun getNextQuestion(): Boolean {
        // Only increment the index if this is not the first question
        if (!isFirstQuestion && _questionIndex.value < level.questions.size) {
            _questionIndex.value += 1
        }
        
        // Mark that we've loaded the first question
        isFirstQuestion = false
        
        // Reset answer result
        _answerResult.value = null
        
        // Check if we've reached the end of questions
        if (_questionIndex.value >= level.questions.size) {
            completeQuiz()
            return false
        }
        
        // Get the next question
        _currentQuestion.value = level.questions[_questionIndex.value]
        return true
    }
    
    /**
     * Processes the user's answer to the current question
     * @param answer The user's selected answer
     * @return AnswerResult containing information about the correctness of the answer
     */
    fun reply(answer: String): AnswerResult {
        val currentQuestion = _currentQuestion.value ?: return AnswerResult(false, answer, "")
        
        val isCorrect = answer == currentQuestion.correctAnswer
        
        // Update score if correct
        if (isCorrect) {
            _score.value += 1
        }
        
        // Save answer to storage
        storageHelper.saveAnswer(level.id, isCorrect)
        
        // Create and store result
        val result = AnswerResult(
            isCorrect = isCorrect,
            givenAnswer = answer,
            correctAnswer = currentQuestion.correctAnswer
        )
        
        _answerResult.value = result
        
        // Check if this is the last question
        if (_questionIndex.value == level.questions.size - 1) {
            completeQuiz()
        }
        
        return result
    }
    
    /**
     * Completes the quiz and updates storage
     */
    private fun completeQuiz() {
        _isCompleted.value = true
        
        // Always mark the level as completed when the quiz is finished
        // The level is considered "passed" if the score meets the threshold
        storageHelper.markLevelCompleted(level.id)
        
        // Log for debugging
        Log.d("QuizViewModel", "Quiz completed. Level ID: ${level.id}, Score: ${_score.value}/${_totalQuestions.value}")
    }
    
    /**
     * Returns the level title
     */
    fun getLevelTitle(): String {
        return level.title
    }
    
    /**
     * Factory for creating the ViewModel with parameters
     */
    class Factory(
        private val storageHelper: StorageHelper,
        private val level: Level
    ) : ViewModelProvider.Factory {
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            if (modelClass.isAssignableFrom(QuizViewModel::class.java)) {
                @Suppress("UNCHECKED_CAST")
                return QuizViewModel(storageHelper, level) as T
            }
            throw IllegalArgumentException("Unknown ViewModel class")
        }
    }
}

/**
 * Data class representing the result of answering a question
 */
data class AnswerResult(
    val isCorrect: Boolean,
    val givenAnswer: String,
    val correctAnswer: String
) 