package com.century.sport.ui.components

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.century.sport.ui.theme.Success
import com.century.sport.ui.theme.SuccessLight
import com.century.sport.ui.theme.Secondary
import com.century.sport.ui.theme.SecondaryLight
import androidx.compose.ui.text.font.FontWeight

// 1. Answer Result Card (Correct/Incorrect)
@Composable
fun AnswerResultCard(
    isCorrect: Boolean,
    text: String,
    value: String,
    modifier: Modifier = Modifier
) {
    val backgroundColor = if (isCorrect) SuccessLight else SecondaryLight
    val contentColor = if (isCorrect) Success else Secondary
    val icon = if (isCorrect) Icons.Default.Check else Icons.Default.Close

    Card(
        modifier = modifier
            .fillMaxWidth()
            .padding(8.dp),
        colors = CardDefaults.cardColors(
            containerColor = backgroundColor
        ),
        shape = RoundedCornerShape(16.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(40.dp)
                    .background(
                        color = if (isCorrect) Success.copy(alpha = 0.1f) else Secondary.copy(alpha = 0.1f),
                        shape = CircleShape
                    ),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = if (isCorrect) "Correct" else "Incorrect",
                    tint = contentColor,
                    modifier = Modifier.size(24.dp)
                )
            }
            
            Spacer(modifier = Modifier.width(16.dp))
            
            Column(
                modifier = Modifier.weight(1f)
            ) {
                Text(
                    text = text,
                    style = MaterialTheme.typography.bodyLarge,
                    color = contentColor
                )
                Text(
                    text = value,
                    style = MaterialTheme.typography.titleMedium,
                    color = contentColor
                )
            }
        }
    }
}

// 2. Game Button - Beautiful button for the main screen
@Composable
fun GameButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Button(
        onClick = onClick,
        modifier = modifier
            .height(64.dp)
            .clip(RoundedCornerShape(32.dp)),
        colors = ButtonDefaults.buttonColors(
            containerColor = MaterialTheme.colorScheme.primary
        ),
        contentPadding = PaddingValues(horizontal = 32.dp)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center
        ) {
            Icon(
                imageVector = Icons.Default.PlayArrow,
                contentDescription = null,
                modifier = Modifier.size(28.dp)
            )
            
            Spacer(modifier = Modifier.width(12.dp))
            
            Text(
                text = text,
                style = MaterialTheme.typography.titleLarge.copy(
                    fontWeight = FontWeight.Bold
                )
            )
        }
    }
}

// 3. Game Selection Button - Card with game name and background ball icons
@Composable
fun GameSelectionButton(
    gameName: String,
    sportIconResId: Int,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    backgroundColor: Color = MaterialTheme.colorScheme.surfaceVariant
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .height(120.dp)
            .padding(8.dp)
            .clickable(onClick = onClick),
        colors = CardDefaults.cardColors(
            containerColor = backgroundColor
        ),
        elevation = CardDefaults.cardElevation(
            defaultElevation = 4.dp
        )
    ) {
        Box(
            modifier = Modifier.fillMaxSize()
        ) {
            // Create a repeating pattern background with 11 columns
            Row(
                modifier = Modifier.fillMaxSize(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                // Create 11 columns of icons with alternating patterns
                for (colIndex in 0..10) {
                    // Alternate between regular and offset columns
                    if (colIndex % 2 == 0) {
                        // Regular column (5 icons)
                        Column(
                            modifier = Modifier.weight(1f)
                        ) {
                            repeat(5) {
                                Image(
                                    painter = painterResource(id = sportIconResId),
                                    contentDescription = null,
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .weight(1f)
                                        .alpha(0.1f)
                                        .padding(2.dp), // Smaller padding for more icons
                                    contentScale = ContentScale.Fit
                                )
                            }
                        }
                    } else {
                        // Offset column (4 icons with spacing)
                        Column(
                            modifier = Modifier.weight(1f),
                            verticalArrangement = Arrangement.Center
                        ) {
                            Spacer(modifier = Modifier.height(12.dp))
                            repeat(4) {
                                Image(
                                    painter = painterResource(id = sportIconResId),
                                    contentDescription = null,
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .weight(1f)
                                        .alpha(0.1f)
                                        .padding(2.dp), // Smaller padding for more icons
                                    contentScale = ContentScale.Fit
                                )
                            }
                            Spacer(modifier = Modifier.height(12.dp))
                        }
                    }
                }
            }
            
            // Game name text with all caps and increased letter spacing
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = gameName.uppercase(),
                    style = MaterialTheme.typography.displayMedium.copy(
                        letterSpacing = 4.sp,
                        fontWeight = FontWeight.W800
                    ),
                    color = MaterialTheme.colorScheme.onSurface,
                    textAlign = TextAlign.Center
                )
            }
        }
    }
} 