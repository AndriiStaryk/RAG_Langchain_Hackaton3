package com.century.sport.ui

import android.content.Context
import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.century.sport.data.StorageHelper
import com.century.sport.model.Level
import com.century.sport.model.Question
import com.century.sport.ui.theme.*
import com.century.sport.viewmodel.AnswerResult
import com.century.sport.viewmodel.QuizViewModel
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.json.Json

class QuizActivity : ComponentActivity() {
    
    private lateinit var level: Level
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        try {
            // Get the level from the intent
            val levelJson = intent.getStringExtra("LEVEL_JSON") ?: run {
                showError("No level data provided")
                return
            }
            
            try {
                level = Json.decodeFromString(levelJson)
            } catch (e: Exception) {
                showError("Failed to parse level data: ${e.message}")
                return
            }
            
            // Initialize StorageHelper
            val storageHelper = StorageHelper(this)
            
            // Initialize ViewModel
            val viewModel: QuizViewModel by viewModels {
                QuizViewModel.Factory(storageHelper, level)
            }
            
            setContent {
                SportsQuizTheme {
                    QuizScreen(
                        viewModel = viewModel,
                        this,
                        level,
                        onBackPressed = {
                            finish()
                        },
                        onComplete = {
                            finish()
                        }
                    )
                }
            }
        } catch (e: Exception) {
            showError("An unexpected error occurred: ${e.message}")
        }
    }
    
    private fun showError(message: String) {
        android.widget.Toast.makeText(this, message, android.widget.Toast.LENGTH_LONG).show()
        finish()
    }
}

@OptIn(ExperimentalMaterial3Api::class, ExperimentalAnimationApi::class)
@Composable
fun QuizScreen(
    viewModel: QuizViewModel,
    context: Context,
    level: Level,
    onBackPressed: () -> Unit,
    onComplete: () -> Unit
) {
    val currentQuestion by viewModel.currentQuestion.collectAsState()
    val questionIndex by viewModel.questionIndex.collectAsState()
    val score by viewModel.score.collectAsState()
    val totalQuestions by viewModel.totalQuestions.collectAsState()
    val answerResult by viewModel.answerResult.collectAsState()
    val isCompleted by viewModel.isCompleted.collectAsState()
    
    // Navigate to result screen when completed
    LaunchedEffect(isCompleted) {
        if (isCompleted) {
            // Dump preferences for debugging
            val storageHelper = StorageHelper(context)
            storageHelper.dumpAllPreferences()
            
            val intent = Intent(context, ResultActivity::class.java).apply {
                putExtra("SCORE", score)
                putExtra("TOTAL_QUESTIONS", totalQuestions)
                putExtra("LEVEL_ID", level.id)
                putExtra("LEVEL_TITLE", viewModel.getLevelTitle())
            }
            context.startActivity(intent)
            onComplete()
        }
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            text = viewModel.getLevelTitle().uppercase(),
                            fontWeight = FontWeight.Bold,
                            style = MaterialTheme.typography.titleMedium
                        )
                        Text(
                            text = "Score: $score",
                            style = MaterialTheme.typography.bodySmall,
                            color = Color.White.copy(alpha = 0.8f)
                        )
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onBackPressed) {
                        Icon(
                            imageVector = Icons.Default.ArrowBack,
                            contentDescription = "Back"
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primary,
                    titleContentColor = Color.White,
                    navigationIconContentColor = Color.White
                ),
                actions = {
                    // Display current score as a badge
                    Box(
                        modifier = Modifier
                            .padding(end = 16.dp)
                            .size(36.dp)
                            .clip(CircleShape)
                            .background(Color.White.copy(alpha = 0.2f)),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = "$questionIndex/$totalQuestions",
                            style = MaterialTheme.typography.bodyMedium,
                            fontWeight = FontWeight.Bold,
                            color = Color.White
                        )
                    }
                }
            )
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .background(
                    Brush.verticalGradient(
                        colors = listOf(
                            MaterialTheme.colorScheme.background,
                            MaterialTheme.colorScheme.background.copy(alpha = 0.95f)
                        )
                    )
                )
        ) {
            // Progress indicator with animation
            val progressAnimation by animateFloatAsState(
                targetValue = questionIndex.toFloat() / totalQuestions,
                animationSpec = tween(500, easing = FastOutSlowInEasing),
                label = "progressAnimation"
            )
            
            LinearProgressIndicator(
                progress = progressAnimation,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(8.dp),
                color = MaterialTheme.colorScheme.primary,
                trackColor = MaterialTheme.colorScheme.surfaceVariant
            )
            
            if (currentQuestion != null) {
                QuestionContent(
                    question = currentQuestion!!,
                    questionNumber = questionIndex + 1,
                    totalQuestions = totalQuestions,
                    answerResult = answerResult,
                    onAnswerSelected = { answer ->
                        if (answerResult == null) {
                            viewModel.reply(answer)
                        }
                    },
                    onNextQuestion = {
                        if (isCompleted) {
                            onComplete()
                        } else {
                            viewModel.getNextQuestion()
                        }
                    }
                )
            } else {
                // Loading or error state
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            }
        }
    }
}

@OptIn(ExperimentalAnimationApi::class)
@Composable
fun QuestionContent(
    question: Question,
    questionNumber: Int,
    totalQuestions: Int,
    answerResult: AnswerResult?,
    onAnswerSelected: (String) -> Unit,
    onNextQuestion: () -> Unit
) {
    // Store the options in a remember block to prevent reshuffling
    val options = remember(question.id) {
        question.getAllOptions()
    }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Question number indicator with animation
        AnimatedVisibility(
            visible = true,
            enter = fadeIn() + expandVertically()
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Question icon
                Box(
                    modifier = Modifier
                        .size(48.dp)
                        .clip(CircleShape)
                        .background(MaterialTheme.colorScheme.primaryContainer),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "$questionNumber",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                }
                
                Spacer(modifier = Modifier.width(16.dp))
                
                Column {
                    Text(
                        text = "Question $questionNumber of $totalQuestions",
                        style = MaterialTheme.typography.titleMedium,
                        color = MaterialTheme.colorScheme.primary,
                        fontWeight = FontWeight.Bold
                    )
                    
                    Text(
                        text = "Select the correct answer",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
        
        // Question card with shadow and rounded corners
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 16.dp)
                .shadow(
                    elevation = 4.dp,
                    shape = RoundedCornerShape(16.dp)
                ),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surface
            ),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(
                modifier = Modifier.padding(20.dp)
            ) {
                // Question text with animation
                AnimatedVisibility(
                    visible = true,
                    enter = fadeIn() + expandVertically()
                ) {
                    Text(
                        text = question.text,
                        style = MaterialTheme.typography.headlineSmall,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onSurface,
                        modifier = Modifier.padding(bottom = 8.dp)
                    )
                }
                
                if (question.year != null) {
                    Text(
                        text = "Year: ${question.year}",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.padding(bottom = 8.dp)
                    )
                }
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Answer options with staggered animation
        Column(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            options.forEachIndexed { index, option ->
                AnimatedVisibility(
                    visible = true,
                    enter = fadeIn(
                        initialAlpha = 0.3f,
                        animationSpec = tween(
                            durationMillis = 300,
                            delayMillis = 100 * index
                        )
                    ) + expandVertically(
                        animationSpec = tween(
                            durationMillis = 300,
                            delayMillis = 100 * index
                        )
                    )
                ) {
                    EnhancedAnswerOption(
                        text = option,
                        isSelected = option == answerResult?.givenAnswer,
                        isCorrect = when {
                            answerResult == null -> null
                            option == answerResult.correctAnswer -> true
                            option == answerResult.givenAnswer -> false
                            else -> null
                        },
                        isEnabled = answerResult == null,
                        onClick = { onAnswerSelected(option) }
                    )
                }
            }
        }
        
        // Answer result and next button
        AnimatedVisibility(
            visible = answerResult != null,
            enter = fadeIn() + expandVertically()
        ) {
            Column {
                Spacer(modifier = Modifier.height(16.dp))
                
                // Result message
                EnhancedResultCard(
                    isCorrect = answerResult?.isCorrect == true,
                    correctAnswer = answerResult?.correctAnswer ?: "",
                    modifier = Modifier.fillMaxWidth()
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                // Next button with animation
                Button(
                    onClick = onNextQuestion,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(56.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.primary
                    ),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.Center
                    ) {
                        Text(
                            text = if (questionNumber < totalQuestions) "NEXT QUESTION" else "COMPLETE!",
                            fontWeight = FontWeight.Bold
                        )
                        
                        Spacer(modifier = Modifier.width(8.dp))
                        
                        Icon(
                            imageVector = if (questionNumber < totalQuestions) 
                                Icons.Default.ArrowForward else Icons.Default.Check,
                            contentDescription = null
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun EnhancedAnswerOption(
    text: String,
    isSelected: Boolean,
    isCorrect: Boolean?,
    isEnabled: Boolean,
    onClick: () -> Unit
) {
    val backgroundColor = when {
        isCorrect == true -> Color(0xFFE8F5E9) // Light green for correct
        isCorrect == false -> Color(0xFFFFEBEE) // Light red for wrong
        isSelected -> MaterialTheme.colorScheme.primaryContainer
        else -> MaterialTheme.colorScheme.surface
    }
    
    val borderColor = when {
        isCorrect == true -> Success
        isCorrect == false -> Secondary
        isSelected -> MaterialTheme.colorScheme.primary
        else -> MaterialTheme.colorScheme.outline
    }
    
    val icon: ImageVector? = when {
        isCorrect == true -> Icons.Default.Check
        isCorrect == false -> Icons.Default.Close
        isSelected -> Icons.Default.Favorite
        else -> null
    }
    
    val elevation = animateDpAsState(
        targetValue = if (isSelected) 8.dp else 2.dp,
        animationSpec = tween(durationMillis = 300),
        label = "elevation"
    )
    
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .then(
                if (isEnabled) {
                    Modifier.clickable(onClick = onClick)
                } else {
                    Modifier
                }
            )
            .border(
                width = 2.dp,
                color = borderColor,
                shape = RoundedCornerShape(12.dp)
            ),
        colors = CardDefaults.cardColors(
            containerColor = backgroundColor
        ),
        elevation = CardDefaults.cardElevation(
            defaultElevation = elevation.value
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            if (isCorrect == true) {
                Box(
                    modifier = Modifier
                        .size(32.dp)
                        .clip(CircleShape)
                        .background(Success.copy(alpha = 0.2f)),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Default.Check,
                        contentDescription = "Correct",
                        tint = Success,
                        modifier = Modifier.size(20.dp)
                    )
                }
                
                Spacer(modifier = Modifier.width(16.dp))
            } else if (isCorrect == false) {
                Box(
                    modifier = Modifier
                        .size(32.dp)
                        .clip(CircleShape)
                        .background(Secondary.copy(alpha = 0.2f)),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Default.Close,
                        contentDescription = "Incorrect",
                        tint = Secondary,
                        modifier = Modifier.size(20.dp)
                    )
                }
                
                Spacer(modifier = Modifier.width(16.dp))
            } else if (isSelected) {
                Box(
                    modifier = Modifier
                        .size(32.dp)
                        .clip(CircleShape)
                        .background(MaterialTheme.colorScheme.primary.copy(alpha = 0.2f)),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Default.Favorite,
                        contentDescription = "Selected",
                        tint = MaterialTheme.colorScheme.primary,
                        modifier = Modifier.size(20.dp)
                    )
                }
                
                Spacer(modifier = Modifier.width(16.dp))
            } else {
                Box(
                    modifier = Modifier
                        .size(32.dp)
                        .clip(CircleShape)
                        .background(MaterialTheme.colorScheme.outline.copy(alpha = 0.1f)),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Default.FavoriteBorder,
                        contentDescription = "Unselected",
                        tint = MaterialTheme.colorScheme.outline,
                        modifier = Modifier.size(20.dp)
                    )
                }
                
                Spacer(modifier = Modifier.width(16.dp))
            }
            
            Text(
                text = text,
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurface,
                modifier = Modifier.weight(1f)
            )
        }
    }
}

@Composable
fun EnhancedResultCard(
    isCorrect: Boolean,
    correctAnswer: String,
    modifier: Modifier = Modifier
) {
    val backgroundColor = if (isCorrect) Color(0xFFE8F5E9) else Color(0xFFFFEBEE)
    val borderColor = if (isCorrect) Success else Secondary
    val icon = if (isCorrect) Icons.Default.Check else Icons.Default.Close
    val title = if (isCorrect) "Correct!" else "Incorrect!"
    
    Card(
        modifier = modifier
            .shadow(
                elevation = 8.dp,
                shape = RoundedCornerShape(16.dp)
            ),
        colors = CardDefaults.cardColors(
            containerColor = backgroundColor
        ),
        border = CardDefaults.outlinedCardBorder().copy(
            width = 2.dp,
            brush = SolidColor(borderColor)
        ),
        shape = RoundedCornerShape(16.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Result icon
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
                    .background(
                        color = if (isCorrect) Success.copy(alpha = 0.2f) else Secondary.copy(alpha = 0.2f)
                    ),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = if (isCorrect) Success else Secondary,
                    modifier = Modifier.size(32.dp)
                )
            }
            
            Spacer(modifier = Modifier.width(16.dp))
            
            // Result text
            Column {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    color = if (isCorrect) Success else Secondary
                )
                
                if (!isCorrect) {
                    Spacer(modifier = Modifier.height(4.dp))
                    
                    Text(
                        text = "Correct answer: $correctAnswer",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
    }
} 