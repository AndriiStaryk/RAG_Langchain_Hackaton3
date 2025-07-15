package com.century.sport.ui.animation

import androidx.compose.animation.core.*
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.size
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.dp
import kotlin.math.cos
import kotlin.math.sin

/**
 * A composable that displays a spiral of sports icons with an animated choreography:
 * 1. Slow spinning spiral
 * 2. Periodic expansion and acceleration
 * 3. Return to normal state
 * 4. Repeat
 */
@Composable
fun SportsIconsSpiral(
    sportIcons: List<Int>,
    modifier: Modifier = Modifier,
    numRepetitions: Int = 20 // Increase the number of icons to create a fuller spiral
) {
    // Animation states
    val infiniteTransition = rememberInfiniteTransition()
    
    // Base rotation animation (continuous slow spin)
    val baseRotation by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(30000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        )
    )
    
    // Expansion/contraction and speed change animation
    val expansionFactor by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = keyframes {
                durationMillis = 6000
                1f at 0
                1.5f at 1500
                1f at 3000
                1f at 6000
            },
            repeatMode = RepeatMode.Restart
        )
    )
    
    // Speed multiplier animation
    val speedMultiplier by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = keyframes {
                durationMillis = 6000
                1f at 0
                3f at 1500
                1f at 3000
                1f at 6000
            },
            repeatMode = RepeatMode.Restart
        )
    )
    
    // Alpha animation for a pulsating effect
    val alpha by infiniteTransition.animateFloat(
        initialValue = 0.2f,
        targetValue = 0.2f,
        animationSpec = infiniteRepeatable(
            animation = keyframes {
                durationMillis = 6000
                0.2f at 0
                0.4f at 1500
                0.2f at 3000
                0.2f at 6000
            },
            repeatMode = RepeatMode.Restart
        )
    )
    
    Box(
        modifier = modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        // Create the spiral of icons
        val totalIcons = numRepetitions * sportIcons.size
        val spiralFactor = 0.5f // Increased to make the spiral more pronounced
        
        for (i in 0 until totalIcons) {
            // Calculate position on spiral
            val angle = i * 15f // Reduced angle between icons for tighter spiral
            val distance = i * spiralFactor // Distance from center increases with each icon
            
            // Apply current animation values
            val currentAngle = angle + baseRotation * speedMultiplier
            val currentDistance = distance * expansionFactor
            
            // Convert polar coordinates to Cartesian
            val x = currentDistance * cos(Math.toRadians(currentAngle.toDouble())).toFloat()
            val y = currentDistance * sin(Math.toRadians(currentAngle.toDouble())).toFloat()
            
            // Size also changes with distance for perspective effect
            val iconSize = (20 + distance * 0.5f).coerceAtMost(50f)
            
            // Individual icon rotation for extra visual interest
            val iconRotation = currentAngle * 0.5f
            
            // Only draw icons that are within a reasonable distance from center
            if (currentDistance < 50) { // Limit how far out the spiral goes
                Image(
                    painter = painterResource(id = sportIcons[i % sportIcons.size]),
                    contentDescription = null,
                    modifier = Modifier
                        .size(iconSize.dp)
                        .alpha(alpha * (1f - currentDistance / 50f)) // Fade out as they get further
                        .graphicsLayer {
                            translationX = x * 8 // Adjusted multiplier
                            translationY = y * 8 // Adjusted multiplier
                            rotationZ = iconRotation
                            scaleX = expansionFactor * 0.8f
                            scaleY = expansionFactor * 0.8f
                        },
                    contentScale = ContentScale.Fit
                )
            }
        }
    }
}

/**
 * A simpler version that uses a single sport icon repeated in the spiral
 */
@Composable
fun SportIconSpiral(
    sportIconResId: Int,
    numIcons: Int = 40, // Increased for fuller spiral
    modifier: Modifier = Modifier
) {
    SportsIconsSpiral(
        sportIcons = List(numIcons) { sportIconResId },
        modifier = modifier
    )
} 