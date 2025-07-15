package com.century.sport.ui

import android.content.Intent
import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.slideInVertically
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.collectAsState
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.ViewModelProvider
import com.century.sport.R
import com.century.sport.data.StorageHelper
import com.century.sport.model.Level
import com.century.sport.model.LevelModel
import com.century.sport.ui.animation.SportsIconsSpiral
import com.century.sport.ui.theme.*
import com.century.sport.viewmodel.LevelState
import com.century.sport.viewmodel.LevelViewModel
import com.century.sport.viewmodel.LevelWithState
import com.century.sport.viewmodel.LevelsUiState
import kotlinx.coroutines.flow.StateFlow
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

class LevelsActivity : ComponentActivity() {
    
    private lateinit var sportName: String
    private var sportOrder: Int = 0
    private var sportIconResId: Int = R.drawable.b1
    private lateinit var storageHelper: StorageHelper
    private lateinit var viewModel: LevelViewModel
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialize StorageHelper
        storageHelper = StorageHelper(this)
        
        // Dump preferences for debugging
        storageHelper.dumpAllPreferences()
        
        // Get the sport order from the intent
        sportOrder = intent.getIntExtra("SPORT_ORDER", 0)
        
        // Set the sport name and icon based on the order
        sportName = when(sportOrder) {
            0 -> "American Football"
            1 -> "Basketball"
            2 -> "Soccer"
            3 -> "Golf"
            4 -> "Tennis"
            else -> "Unknown Sport"
        }
        
        sportIconResId = when(sportOrder) {
            0 -> R.drawable.b1
            1 -> R.drawable.b3
            2 -> R.drawable.b4
            3 -> R.drawable.b5
            4 -> R.drawable.b2
            else -> R.drawable.b1
        }
        
        // Initialize ViewModel
        viewModel = ViewModelProvider(this, LevelViewModel.Factory(storageHelper, sportOrder))[LevelViewModel::class.java]
        
        setContent {
            SportsQuizTheme {
                LevelsScreen(
                    sportName = sportName,
                    sportIconResId = sportIconResId,
                    viewModel = viewModel,
                    onLevelSelected = { level ->
                        // Navigate to the quiz screen with the selected level
                        val intent = Intent(this, QuizActivity::class.java)
                        val levelJson = Json.encodeToString(Level.serializer(), level)
                        intent.putExtra("LEVEL_JSON", levelJson)
                        startActivity(intent)
                    },
                    onBackPressed = {
                        finish()
                    }
                )
            }
        }
    }
    
    override fun onResume() {
        super.onResume()
        Log.d("LevelsActivity", "onResume called, refreshing data")
        
        // Refresh the data when returning to this screen
        viewModel.refreshLevels()
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LevelsScreen(
    sportName: String,
    sportIconResId: Int,
    viewModel: LevelViewModel,
    onLevelSelected: (Level) -> Unit,
    onBackPressed: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        text = sportName.uppercase(),
                        fontWeight = FontWeight.Bold
                    )
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
                )
            )
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            when (uiState) {
                is LevelsUiState.Loading -> {
                    // Show loading indicator
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        CircularProgressIndicator()
                    }
                }
                
                is LevelsUiState.Success -> {
                    val levels = (uiState as LevelsUiState.Success).levels
                    
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(16.dp)
                    ) {
                        // Sport icon and title
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(bottom = 24.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Image(
                                painter = painterResource(id = sportIconResId),
                                contentDescription = sportName,
                                modifier = Modifier
                                    .size(64.dp)
                                    .clip(CircleShape)
                                    .background(MaterialTheme.colorScheme.primaryContainer)
                                    .padding(8.dp)
                            )
                            
                            Spacer(modifier = Modifier.width(16.dp))
                            
                            Column {
                                Text(
                                    text = sportName,
                                    style = MaterialTheme.typography.headlineSmall,
                                    fontWeight = FontWeight.Bold,
                                    color = MaterialTheme.colorScheme.onBackground
                                )
                                
                                Text(
                                    text = "${levels.count { it.state == LevelState.PASSED }}/${levels.size} levels completed",
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                        }
                        
                        // Level list
                        LazyColumn(
                            modifier = Modifier.fillMaxSize(),
                            verticalArrangement = Arrangement.spacedBy(16.dp)
                        ) {
                            itemsIndexed(levels) { index, levelWithState ->
                                EnhancedLevelCard(
                                    levelWithState = levelWithState,
                                    onClick = {
                                        if (levelWithState.state != LevelState.LOCKED) {
                                            onLevelSelected(levelWithState.level)
                                        }
                                    }
                                )
                                
                                // Add a connector line between levels
                                if (index < levels.size - 1) {
                                    Box(
                                        modifier = Modifier
                                            .padding(start = 24.dp)
                                            .width(2.dp)
                                            .height(16.dp)
                                            .background(
                                                color = when {
                                                    levelWithState.state == LevelState.PASSED -> Success
                                                    else -> MaterialTheme.colorScheme.outline.copy(alpha = 0.5f)
                                                }
                                            )
                                    )
                                }
                            }
                        }
                    }
                }
                
                is LevelsUiState.Error -> {
                    // Show error message
                    Box(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(16.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = (uiState as LevelsUiState.Error).message,
                            style = MaterialTheme.typography.bodyLarge,
                            color = MaterialTheme.colorScheme.error,
                            textAlign = TextAlign.Center
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun EnhancedLevelCard(
    levelWithState: LevelWithState,
    onClick: () -> Unit
) {
    val level = levelWithState.level
    val state = levelWithState.state
    
    val isPassed = state == LevelState.PASSED
    val isUnlocked = state == LevelState.UNLOCKED
    val isLocked = state == LevelState.LOCKED
    
    val backgroundColor = when (state) {
        LevelState.PASSED -> Color(0xFFE8F5E9) // Light green
        LevelState.UNLOCKED -> MaterialTheme.colorScheme.surface
        LevelState.LOCKED -> Color(0xFFF5F5F5) // Light gray
    }
    
    val contentAlpha = if (isLocked) 0.5f else 1f
    
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(16.dp))
            .then(
                if (!isLocked) {
                    Modifier.clickable(onClick = onClick)
                } else {
                    Modifier
                }
            ),
        colors = CardDefaults.cardColors(
            containerColor = backgroundColor
        ),
        elevation = CardDefaults.cardElevation(
            defaultElevation = if (isLocked) 1.dp else 4.dp
        ),
        border = if (isPassed) {
            BorderStroke(2.dp, Success)
        } else {
            null
        }
    ) {
        Row(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Level status icon
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
                    .background(
                        color = when (state) {
                            LevelState.PASSED -> Success
                            LevelState.UNLOCKED -> Primary
                            LevelState.LOCKED -> Color.Gray
                        }
                    ),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = when (state) {
                        LevelState.PASSED -> Icons.Default.Check
                        LevelState.UNLOCKED -> Icons.Default.PlayArrow
                        LevelState.LOCKED -> Icons.Default.Lock
                    },
                    contentDescription = when (state) {
                        LevelState.PASSED -> "Completed"
                        LevelState.UNLOCKED -> "Play"
                        LevelState.LOCKED -> "Locked"
                    },
                    tint = Color.White,
                    modifier = Modifier.size(24.dp)
                )
            }
            
            Spacer(modifier = Modifier.width(16.dp))
            
            // Level info
            Column(
                modifier = Modifier
                    .weight(1f)
                    .alpha(contentAlpha)
            ) {
                Text(
                    text = level.title,
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                
                Spacer(modifier = Modifier.height(4.dp))
                
                // Difficulty indicator
                Row(
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Difficulty: ",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    
                    // Show stars based on difficulty
                    val difficultyStars = when(level.difficulty.lowercase()) {
                        "easy" -> 1
                        "medium" -> 2
                        "hard" -> 3
                        else -> 1
                    }
                    
                    repeat(difficultyStars) {
                        Icon(
                            imageVector = Icons.Default.Star,
                            contentDescription = null,
                            tint = if (isPassed) Success else Primary,
                            modifier = Modifier
                                .size(16.dp)
                                .padding(end = 2.dp)
                        )
                    }
                }
                
                // Show completion status
                if (isPassed) {
                    Spacer(modifier = Modifier.height(4.dp))
                    
                    Text(
                        text = "COMPLETED",
                        style = MaterialTheme.typography.labelMedium,
                        color = Success,
                        fontWeight = FontWeight.Bold
                    )
                } else if (isLocked) {
                    Spacer(modifier = Modifier.height(4.dp))
                    
                    Text(
                        text = "COMPLETE PREVIOUS LEVEL TO UNLOCK",
                        style = MaterialTheme.typography.labelSmall,
                        color = Color.Gray,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
            
            // Progress indicator for completed levels
            if (isPassed && levelWithState.progress != null) {
                val progress = levelWithState.progress
                val correctAnswers = progress.correctAnswers
                val totalAnswers = progress.correctAnswers + progress.wrongAnswers
                
                if (totalAnswers > 0) {
                    Column(
                        horizontalAlignment = Alignment.End
                    ) {
                        Text(
                            text = "$correctAnswers/$totalAnswers",
                            style = MaterialTheme.typography.titleMedium,
                            color = Success,
                            fontWeight = FontWeight.Bold
                        )
                        
                        Text(
                            text = "correct",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
        }
    }
} 