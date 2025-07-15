package com.century.sport.ui.animation

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.century.sport.R
import com.century.sport.ui.theme.Primary
import com.century.sport.ui.theme.PrimaryLight
import com.century.sport.ui.theme.SportsQuizTheme

class AnimationDemoActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            SportsQuizTheme {
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
                    // Background spiral animation
                    SportsIconsSpiral(
                        sportIcons = listOf(
                            R.drawable.b1,
                            R.drawable.b2,
                            R.drawable.b3,
                            R.drawable.b4
                        ),
                        numRepetitions = 30 // More repetitions for a fuller spiral
                    )
                    
//                    // Content on top of the animation
//                    Column(
//                        modifier = Modifier
//                            .fillMaxSize()
//                            .padding(16.dp),
//                        horizontalAlignment = Alignment.CenterHorizontally,
//                        verticalArrangement = Arrangement.Center
//                    ) {
//                        Card(
//                            modifier = Modifier
//                                .padding(16.dp),
//                            colors = CardDefaults.cardColors(
//                                containerColor = MaterialTheme.colorScheme.surface.copy(alpha = 0.9f)
//                            ),
//                            elevation = CardDefaults.cardElevation(
//                                defaultElevation = 8.dp
//                            )
//                        ) {
//                            Column(
//                                modifier = Modifier
//                                    .padding(24.dp),
//                                horizontalAlignment = Alignment.CenterHorizontally
//                            ) {
//                                Text(
//                                    text = "SPORTS QUIZ",
//                                    fontSize = 36.sp,
//                                    fontWeight = FontWeight.Bold,
//                                    color = MaterialTheme.colorScheme.primary,
//                                    textAlign = TextAlign.Center
//                                )
//
//                                Spacer(modifier = Modifier.height(16.dp))
//
//                                Text(
//                                    text = "Test your knowledge with our animated sports quiz!",
//                                    fontSize = 16.sp,
//                                    color = MaterialTheme.colorScheme.onSurface,
//                                    textAlign = TextAlign.Center
//                                )
//
//                                Spacer(modifier = Modifier.height(24.dp))
//
//                                Button(
//                                    onClick = { /* Navigate to main activity */ },
//                                    modifier = Modifier
//                                        .fillMaxWidth()
//                                        .height(56.dp),
//                                    colors = ButtonDefaults.buttonColors(
//                                        containerColor = Primary
//                                    )
//                                ) {
//                                    Text(
//                                        text = "START QUIZ",
//                                        fontWeight = FontWeight.Bold
//                                    )
//                                }
//                            }
//                        }
//                    }
                }
            }
        }
    }
} 