package com.century.sport.ui

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.*
import androidx.compose.animation.fadeIn
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.century.sport.R
import com.century.sport.data.StorageHelper
import com.century.sport.ui.components.AnswerResultCard
import com.century.sport.ui.components.GameButton
import com.century.sport.ui.theme.*
import com.century.sport.ui.animation.SportsIconsSpiral

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialize StorageHelper
        val storageHelper = StorageHelper(this)
        
        // Check if we should animate the entrance
        val shouldFadeIn = intent.getBooleanExtra("FADE_IN", false)
        
        setContent {
            SportsQuizTheme {
                EnhancedMainScreen(
                    shouldFadeIn = shouldFadeIn,
                    playerStats = storageHelper.getPlayerStats(),
                    onPlayClicked = {
                        // Navigate to the games selection screen
                        val intent = Intent(this, GamesActivity::class.java)
                        startActivity(intent)
                    }
                )
            }
        }
    }
}

@Composable
fun EnhancedMainScreen(
    shouldFadeIn: Boolean,
    playerStats: com.century.sport.model.PlayerStats,
    onPlayClicked: () -> Unit
) {
    // Control visibility state for animation
    var visible by remember { mutableStateOf(!shouldFadeIn) }
    
    // Animation values
    val infiniteTransition = rememberInfiniteTransition()
    val trophyScale by infiniteTransition.animateFloat(
        initialValue = 0.95f,
        targetValue = 1.05f,
        animationSpec = infiniteRepeatable(
            animation = tween(2000, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        )
    )
    
    // If we should animate, start invisible and become visible after composition
    LaunchedEffect(key1 = shouldFadeIn) {
        if (shouldFadeIn) {
            visible = true
        }
    }
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                brush = Brush.verticalGradient(
                    colors = listOf(
                        MaterialTheme.colorScheme.background,
                        MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.3f)
                    )
                )
            )
    ) {
        // Add the spiral animation as background
        SportsIconsSpiral(
            sportIcons = listOf(
                R.drawable.b1,
                R.drawable.b2,
                R.drawable.b3,
                R.drawable.b4
            ),
            modifier = Modifier.alpha(0.15f) // Make it subtle
        )
        
        AnimatedVisibility(
            visible = visible,
            enter = fadeIn(animationSpec = tween(durationMillis = 500))
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // Trophy icon with glow effect
                Box(
                    modifier = Modifier
                        .padding(top = 32.dp, bottom = 16.dp)
                        .size(140.dp)
                        .shadow(
                            elevation = 8.dp,
                            shape = CircleShape,
                            spotColor = MaterialTheme.colorScheme.primary
                        )
                        .background(
                            brush = Brush.radialGradient(
                                colors = listOf(
                                    MaterialTheme.colorScheme.primaryContainer,
                                    MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.6f)
                                )
                            ),
                            shape = CircleShape
                        ),
                    contentAlignment = Alignment.Center
                ) {
                    Image(
                        painter = painterResource(id = R.drawable.ic_trophy),
                        contentDescription = "Trophy",
                        modifier = Modifier
                            .size(100.dp)
                            .graphicsLayer {
                                scaleX = trophyScale
                                scaleY = trophyScale
                            }
                    )
                }
                
                // App name with stylish text
                Text(
                    text = "CENTURY OF SPORT",
                    style = MaterialTheme.typography.displayMedium.copy(
                        fontWeight = FontWeight.ExtraBold,
                        letterSpacing = 2.sp
                    ),
                    textAlign = TextAlign.Center,
                    color = MaterialTheme.colorScheme.primary
                )
                
                Text(
                    text = "Test your sports knowledge!",
                    style = MaterialTheme.typography.titleMedium,
                    textAlign = TextAlign.Center,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.padding(bottom = 32.dp)
                )
                
                // Stats section with title
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 8.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.surface
                    ),
                    elevation = CardDefaults.cardElevation(
                        defaultElevation = 4.dp
                    ),
                    shape = RoundedCornerShape(16.dp)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = "YOUR STATS",
                            style = MaterialTheme.typography.titleMedium.copy(
                                fontWeight = FontWeight.Bold,
                                letterSpacing = 1.sp
                            ),
                            color = MaterialTheme.colorScheme.primary,
                            modifier = Modifier.padding(bottom = 16.dp)
                        )
                        
                        // Stats cards in a row
                        Row(
                            modifier = Modifier
                                .fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            // Correct answers card
                            AnswerResultCard(
                                isCorrect = true,
                                text = "Correct",
                                value = playerStats.totalCorrectAnswers.toString(),
                                modifier = Modifier.weight(1f)
                            )
                            
                            Spacer(modifier = Modifier.width(12.dp))
                            
                            // Incorrect answers card
                            AnswerResultCard(
                                isCorrect = false,
                                text = "Wrong",
                                value = playerStats.totalWrongAnswers.toString(),
                                modifier = Modifier.weight(1f)
                            )
                        }
                        
                        Spacer(modifier = Modifier.height(16.dp))
                        
                        // Levels completed with icon
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(12.dp))
                                .background(
                                    brush = Brush.horizontalGradient(
                                        colors = listOf(
                                            PrimaryLight,
                                            Primary
                                        )
                                    )
                                )
                                .padding(16.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.Center
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(40.dp)
                                    .background(
                                        color = Color.White.copy(alpha = 0.2f),
                                        shape = CircleShape
                                    ),
                                contentAlignment = Alignment.Center
                            ) {
                                Icon(
                                    imageVector = Icons.Default.Star,
                                    contentDescription = null,
                                    tint = Color.White,
                                    modifier = Modifier.size(24.dp)
                                )
                            }
                            
                            Spacer(modifier = Modifier.width(16.dp))
                            
                            Column(
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                Text(
                                    text = "Levels Completed",
                                    style = MaterialTheme.typography.titleMedium,
                                    color = Color.White
                                )
                                
                                Text(
                                    text = playerStats.levelsCompleted.toString(),
                                    style = MaterialTheme.typography.displayMedium,
                                    color = Color.White,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }
                    }
                }
                
                // Accuracy card
                val totalAnswers = playerStats.totalCorrectAnswers + playerStats.totalWrongAnswers
                val accuracy = if (totalAnswers > 0) {
                    (playerStats.totalCorrectAnswers.toFloat() / totalAnswers) * 100
                } else {
                    0f
                }
                
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 16.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.surface
                    ),
                    elevation = CardDefaults.cardElevation(
                        defaultElevation = 4.dp
                    ),
                    shape = RoundedCornerShape(16.dp)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = "ACCURACY",
                            style = MaterialTheme.typography.titleMedium.copy(
                                fontWeight = FontWeight.Bold,
                                letterSpacing = 1.sp
                            ),
                            color = MaterialTheme.colorScheme.primary
                        )
                        
                        Text(
                            text = "${accuracy.toInt()}%",
                            style = MaterialTheme.typography.displayLarge,
                            color = when {
                                accuracy >= 80 -> Success
                                accuracy >= 50 -> Primary
                                else -> Secondary
                            },
                            fontWeight = FontWeight.Bold
                        )
                        
                        Text(
                            text = "Total Questions: $totalAnswers",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
                
                Spacer(modifier = Modifier.weight(1f))
                
                // Play button with pulsating effect
                GameButton(
                    text = "PLAY NOW",
                    onClick = onPlayClicked,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(bottom = 32.dp)
                )
            }
        }
    }
} 