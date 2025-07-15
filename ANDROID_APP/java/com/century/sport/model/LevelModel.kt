package com.century.sport.model

/**
 * A wrapper class that combines a Level with its completion status
 */
data class LevelModel(
    val level: Level,
    val passed: Boolean = false,
    val isUnlocked: Boolean = false
)
