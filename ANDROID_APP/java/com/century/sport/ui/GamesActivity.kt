package com.century.sport.ui

import android.content.Intent
import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.slideInVertically
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.century.sport.R
import com.century.sport.ui.animation.SportsIconsSpiral
import com.century.sport.ui.components.GameSelectionButton
import com.century.sport.ui.theme.SportsQuizTheme

class GamesActivity : ComponentActivity() {
    
    // Define our game categories
    private val gameCategories = listOf(
        GameCategory("American Football", R.drawable.b1, Color(0xFFE3F2FD)), // Light blue
        GameCategory("Basketball", R.drawable.b3, Color(0xFFFCE4EC)),        // Light pink
        GameCategory("Soccer", R.drawable.b4, Color(0xFFE8F5E9)),            // Light green
        GameCategory("Golf", R.drawable.b5, Color(0xFFFFF3E0)),              // Light orange
        GameCategory("Tennis", R.drawable.b2, Color(0xFFEDE7F6))             // Light purple
    )
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        setContent {
            SportsQuizTheme {
                GamesScreen(
                    gameCategories = gameCategories,
                    onGameSelected = { gameName, order ->
                        Log.d("GamesActivity", "Selected game: $gameName")
                        // Navigate to the levels screen
                        val intent = Intent(this, LevelsActivity::class.java)
                        intent.putExtra("SPORT_ORDER", order)
                        startActivity(intent)
                    },
                    onBackPressed = {
                        finish()
                    }
                )
            }
        }
    }
}

data class GameCategory(
    val name: String,
    val iconResId: Int,
    val backgroundColor: Color
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GamesScreen(
    gameCategories: List<GameCategory>,
    onGameSelected: (String, Int) -> Unit,
    onBackPressed: () -> Unit
) {
    var visible by remember { mutableStateOf(false) }
    
    LaunchedEffect(key1 = Unit) {
        visible = true
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        text = "SELECT A SPORT",
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
            // Background spiral animation (subtle)
            SportsIconsSpiral(
                sportIcons = gameCategories.map { it.iconResId },
                modifier = Modifier.alpha(0.05f),
                numRepetitions = 10
            )
            
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = "Choose a sport category to test your knowledge!",
                    style = MaterialTheme.typography.bodyLarge,
                    textAlign = TextAlign.Center,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.padding(bottom = 24.dp)
                )
                
                LazyColumn(
                    modifier = Modifier.fillMaxWidth(),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    itemsIndexed(gameCategories) { index, category ->
                        AnimatedVisibility(
                            visible = visible,
                            enter = fadeIn(tween(durationMillis = 400, delayMillis = 100 * index)) +
                                    slideInVertically(
                                        tween(durationMillis = 500, delayMillis = 100 * index, 
                                              easing = FastOutSlowInEasing)
                                    ) { it / 3 }
                        ) {
                            GameSelectionButton(
                                gameName = category.name,
                                sportIconResId = category.iconResId,
                                backgroundColor = category.backgroundColor,
                                onClick = { onGameSelected(category.name, index) }
                            )
                        }
                    }
                }
            }
        }
    }
} 