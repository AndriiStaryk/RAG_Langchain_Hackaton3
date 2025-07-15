package com.century.sport.ui

import android.content.Intent
import android.os.Bundle
import android.view.animation.OvershootInterpolator
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.core.*
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.size
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.dp
import com.century.sport.R
import com.century.sport.ui.theme.SportsQuizTheme
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

class LauncherActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            SportsQuizTheme {
                LauncherScreen(
                    onAnimationFinished = {
                        // Navigate to MainActivity when animation completes
                        val intent = Intent(this, MainActivity::class.java)
                        // Add a flag to enable fade-in transition for MainActivity
                        intent.putExtra("FADE_IN", true)
                        startActivity(intent)
                        // Apply a fade-out transition for this activity
                        overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out)
                        finish()
                    }
                )
            }
        }
    }
}

@Composable
fun LauncherScreen(onAnimationFinished: () -> Unit) {
    val coroutineScope = rememberCoroutineScope()
    
    // Get screen dimensions to calculate final scale
    val configuration = LocalConfiguration.current
    val screenWidth = configuration.screenWidthDp.dp.value
    val screenHeight = configuration.screenHeightDp.dp.value
    val iconSize = 200f // Initial icon size in dp
    
    // Calculate how much to scale to cover the entire screen
    // We want the icon to be at least 3x the screen size at the end
    val maxDimension = maxOf(screenWidth, screenHeight)
    val finalScale = (maxDimension * 4) / iconSize
    
    // Animation states
    val scale = remember { Animatable(0.8f) } // Start slightly smaller
    val alpha = remember { Animatable(0f) }
    
    // Launch animations when the composable is first created
    LaunchedEffect(key1 = true) {
        // Step 1: Icon appears (200ms)
        alpha.animateTo(
            targetValue = 1f,
            animationSpec = tween(
                durationMillis = 200,
                easing = LinearEasing
            )
        )
        
        // Step 2: Icon expands to cover the full screen (600ms)
        scale.animateTo(
            targetValue = finalScale,
            animationSpec = tween(
                durationMillis = 600,
                easing = FastOutLinearInEasing
            )
        )
        
        // Step 3: Trigger transition to MainActivity
        onAnimationFinished()
    }
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.primary),
        contentAlignment = Alignment.Center
    ) {
        // Trophy icon with animation applied
        Image(
            painter = painterResource(id = R.drawable.ic_trophy),
            contentDescription = "Sports Quiz Trophy",
            contentScale = ContentScale.Fit,
            modifier = Modifier
                .size(200.dp)
                .alpha(alpha.value)
                .graphicsLayer {
                    scaleX = scale.value
                    scaleY = scale.value
                }
        )
    }
}

// Extension function to convert Android's Interpolator to Compose's Easing
private fun android.view.animation.Interpolator.toEasing() = Easing { x ->
    getInterpolation(x)
} 