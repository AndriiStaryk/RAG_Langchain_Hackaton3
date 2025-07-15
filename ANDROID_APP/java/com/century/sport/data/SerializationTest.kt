package com.century.sport.data

import android.util.Log
import com.century.sport.model.Level
import com.century.sport.model.Question
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

object SerializationTest {
    fun testSerialization() {
        val question = Question(
            id = 491,
            text = "Which team won the first Super Bowl in 1967?",
            correctAnswer = "Green Bay Packers",
            wrongAnswers = listOf(
                "Kansas City Chiefs",
                "Dallas Cowboys",
                "Miami Dolphins"
            ),
            year = 1967
        )
        
        val level = Level(
            id = 50,
            title = "Super Bowl History",
            difficulty = "professional",
            questions = listOf(question)
        )
        
        val json = Json { prettyPrint = true }
        val jsonString = json.encodeToString(level)
        
        Log.d("SerializationTest", "Serialized level: $jsonString")
    }
} 