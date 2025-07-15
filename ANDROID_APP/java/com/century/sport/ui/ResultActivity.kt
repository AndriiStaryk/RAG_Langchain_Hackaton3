package com.century.sport.ui

import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.draw.scale
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.century.sport.ui.theme.Primary
import com.century.sport.ui.theme.Secondary
import com.century.sport.ui.theme.SportsQuizTheme
import com.century.sport.ui.theme.Success
import kotlinx.coroutines.delay
import kotlin.math.cos
import kotlin.math.sin

class ResultActivity : ComponentActivity() {
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Get data from intent
        val score = intent.getIntExtra("SCORE", 0)
        val totalQuestions = intent.getIntExtra("TOTAL_QUESTIONS", 0)
        val levelId = intent.getIntExtra("LEVEL_ID", -1)
        val levelTitle = intent.getStringExtra("LEVEL_TITLE") ?: "Level"
        
        // Calculate if the level is passed based on score
        val passThreshold = 0.7 // 70% correct to pass
        val isPassed = score >= (totalQuestions * passThreshold).toInt()
        
        // Log for debugging
        Log.d("ResultActivity", "Level ID: $levelId, Score: $score/$totalQuestions, Passed: $isPassed")
        
        setContent {
            SportsQuizTheme {
                ResultScreen(
                    score = score,
                    totalQuestions = totalQuestions,
                    isPassed = isPassed,
                    levelTitle = levelTitle,
                    onBackToLevels = {
                        finish()
                    }
                )
            }
        }
    }
}

@OptIn(ExperimentalAnimationApi::class)
@Composable
fun ResultScreen(
    score: Int,
    totalQuestions: Int,
    isPassed: Boolean,
    levelTitle: String,
    onBackToLevels: () -> Unit
) {
    val percentCorrect = (score.toFloat() / totalQuestions) * 100
    
    // Animation states
    var showContent by remember { mutableStateOf(false) }
    var showConfetti by remember { mutableStateOf(false) }
    
    // Start animations after a short delay
    LaunchedEffect(key1 = Unit) {
        delay(300)
        showContent = true
        delay(500)
        showConfetti = true
    }
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    colors = listOf(
                        MaterialTheme.colorScheme.background,
                        if (isPassed) Color(0xFFF1F8E9) else Color(0xFFFCE4EC)
                    )
                )
            )
    ) {
        // Confetti animation for passed levels
        if (isPassed && showConfetti) {
            ConfettiAnimation(
                modifier = Modifier.fillMaxSize()
            )
        }
        
        // Main content
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            AnimatedVisibility(
                visible = showContent,
                enter = fadeIn(tween(500)) + expandVertically(tween(500))
            ) {
                Text(
                    text = if (isPassed) "CONGRATULATIONS!" else "NICE TRY!",
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold,
                    color = if (isPassed) Success else Secondary,
                    textAlign = TextAlign.Center
                )
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            AnimatedVisibility(
                visible = showContent,
                enter = fadeIn(tween(500, delayMillis = 300)) + expandVertically(tween(500, delayMillis = 300))
            ) {
                Text(
                    text = levelTitle,
                    style = MaterialTheme.typography.titleLarge,
                    color = MaterialTheme.colorScheme.onBackground,
                    textAlign = TextAlign.Center
                )
            }
            
            Spacer(modifier = Modifier.height(32.dp))
            
            // Trophy or star icon with animation
            AnimatedVisibility(
                visible = showContent,
                enter = fadeIn(tween(800, delayMillis = 500)) + 
                        scaleIn(tween(800, delayMillis = 500, easing = EaseOutBack))
            ) {
                Box(
                    modifier = Modifier
                        .size(160.dp)
                        .clip(CircleShape)
                        .background(
                            color = if (isPassed) Success.copy(alpha = 0.1f) else Secondary.copy(alpha = 0.1f)
                        ),
                    contentAlignment = Alignment.Center
                ) {
                    val infiniteTransition = rememberInfiniteTransition(label = "iconAnimation")
                    val scale by infiniteTransition.animateFloat(
                        initialValue = 1f,
                        targetValue = 1.1f,
                        animationSpec = infiniteRepeatable(
                            animation = tween(1000, easing = EaseInOutQuad),
                            repeatMode = RepeatMode.Reverse
                        ),
                        label = "scale"
                    )
                    
                    val rotation by infiniteTransition.animateFloat(
                        initialValue = -5f,
                        targetValue = 5f,
                        animationSpec = infiniteRepeatable(
                            animation = tween(2000, easing = EaseInOutQuad),
                            repeatMode = RepeatMode.Reverse
                        ),
                        label = "rotation"
                    )
                    
                    Icon(
                        imageVector = if (isPassed) Icons.Default.CheckCircle else Icons.Default.Star,
                        contentDescription = null,
                        tint = if (isPassed) Success else Secondary,
                        modifier = Modifier
                            .size(100.dp)
                            .scale(scale)
                            .rotate(rotation)
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(32.dp))
            
            // Score display with animation
            AnimatedVisibility(
                visible = showContent,
                enter = fadeIn(tween(500, delayMillis = 800)) + expandVertically(tween(500, delayMillis = 800))
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "YOUR SCORE",
                        style = MaterialTheme.typography.titleMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        fontWeight = FontWeight.Bold
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Row(
                        verticalAlignment = Alignment.Bottom
                    ) {
                        Text(
                            text = "$score",
                            style = MaterialTheme.typography.displayLarge,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary
                        )
                        
                        Text(
                            text = "/$totalQuestions",
                            style = MaterialTheme.typography.headlineMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.padding(bottom = 8.dp, start = 4.dp)
                        )
                    }
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Text(
                        text = "${percentCorrect.toInt()}%",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.Bold,
                        color = if (isPassed) Success else Secondary
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Text(
                        text = if (isPassed) "Level Completed!" else "Try Again!",
                        style = MaterialTheme.typography.titleMedium,
                        color = if (isPassed) Success else Secondary,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
            
            Spacer(modifier = Modifier.weight(1f))
            
            // Back to levels button
            AnimatedVisibility(
                visible = showContent,
                enter = fadeIn(tween(500, delayMillis = 1000)) + expandVertically(tween(500, delayMillis = 1000))
            ) {
                Button(
                    onClick = onBackToLevels,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(56.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.primary
                    )
                ) {
                    Text(
                        text = "BACK TO LEVELS",
                        fontWeight = FontWeight.Bold
                    )
                }
            }
        }
    }
}

@Composable
fun ConfettiAnimation(modifier: Modifier = Modifier) {
    val colors = listOf(Primary, Success, Color(0xFFFFC107), Color(0xFF2196F3), Color(0xFFE91E63))
    
    val infiniteTransition = rememberInfiniteTransition(label = "confetti")
    val animationProgress by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(10000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "confettiProgress"
    )
    
    Canvas(modifier = modifier) {
        val canvasWidth = size.width
        val canvasHeight = size.height
        
        // Create 50 confetti pieces
        repeat(50) { i ->
            val color = colors[i % colors.size]
            val x = (i * 17 % canvasWidth) + cos(animationProgress * 2 * Math.PI + i) * 50
            val y = (animationProgress * canvasHeight * 1.5f) - (i * 23 % 300)
            val size = 15f + (i % 10)
            
            // Draw different shapes for variety
            when (i % 3) {
                0 -> {
                    // Rectangle
                    drawRect(
                        color = color,
                        topLeft = Offset(x.toFloat(), y.toFloat()),
                        size = androidx.compose.ui.geometry.Size(size, size / 2),
                        alpha = 0.7f
                    )
                }
                1 -> {
                    // Circle
                    drawCircle(
                        color = color,
                        radius = size / 2,
                        center = Offset(x.toFloat(), y.toFloat()),
                        alpha = 0.7f
                    )
                }
                else -> {
                    // Star
                    val path = Path()
                    val outerRadius = size / 2
                    val innerRadius = size / 4
                    
                    for (j in 0 until 10) {
                        val radius = if (j % 2 == 0) outerRadius else innerRadius
                        val angle = j * 36f * (Math.PI / 180f)
                        val xPoint = x.toFloat() + radius * cos(angle).toFloat()
                        val yPoint = y.toFloat() + radius * sin(angle).toFloat()
                        
                        if (j == 0) {
                            path.moveTo(xPoint, yPoint)
                        } else {
                            path.lineTo(xPoint, yPoint)
                        }
                    }
                    path.close()
                    
                    drawPath(
                        path = path,
                        color = color,
                        alpha = 0.7f,
                        style = Stroke(width = 2f)
                    )
                }
            }
        }
    }
} 