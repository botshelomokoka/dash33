//! Dash33: AI-powered Bitcoin Dashboard and Analytics Platform
//!
//! This module provides advanced analytics and visualization capabilities for
//! Bitcoin network data, user metrics, and system performance.
//!
//! # Features
//!
//! - Real-time Bitcoin network analytics
//! - Advanced ML-powered predictions
//! - User behavior analysis
//! - System health monitoring
//! - Interactive visualizations
//!
//! # Architecture
//!
//! The dashboard is built on a modular architecture:
//! - Core analytics engine
//! - REST API endpoints
//! - Real-time data processing
//! - ML model integration
//! - Database management
//!
//! # Example
//!
//! ```rust
//! use dash33::{DashboardConfig, AnalyticsLevel, init};
//!
//! #[tokio::main]
//! async fn main() -> Result<(), Box<dyn std::error::Error>> {
//!     let config = DashboardConfig {
//!         network: bitcoin::Network::Bitcoin,
//!         analytics_level: AnalyticsLevel::Advanced,
//!         ..Default::default()
//!     };
//!
//!     let dashboard = init(config)?;
//!     dashboard.run().await?;
//!
//!     Ok(())
//! }
//! ```

#![warn(missing_docs)]
#![warn(rustdoc::missing_doc_code_examples)]
#![forbid(unsafe_code)]
#![deny(clippy::all)]
#![deny(clippy::cargo)]
#![deny(clippy::nursery)]

use std::sync::Arc;
use bitcoin::Network;
use serde::{Serialize, Deserialize};
use axum::{
    routing::{get, post},
    Router,
    Json,
    extract::State,
};
use sqlx::PgPool;
use tower_http::cors::{CorsLayer, Any};
use tracing::{info, error, warn, debug};

/// Dashboard configuration options
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DashboardConfig {
    /// Bitcoin network to connect to
    pub network: Network,
    /// Level of analytics complexity
    pub analytics_level: AnalyticsLevel,
    /// Database configuration
    pub database_url: String,
    /// API configuration
    pub api_config: ApiConfig,
    /// ML model configuration
    pub ml_config: MLConfig,
}

/// API configuration options
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ApiConfig {
    /// Host address
    pub host: String,
    /// Port number
    pub port: u16,
    /// Enable CORS
    pub cors_enabled: bool,
    /// Rate limiting configuration
    pub rate_limit: RateLimit,
}

/// Rate limiting configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RateLimit {
    /// Requests per second
    pub requests_per_second: u32,
    /// Burst size
    pub burst_size: u32,
}

/// ML model configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MLConfig {
    /// Model type
    pub model_type: String,
    /// Training interval in seconds
    pub training_interval: u64,
    /// Minimum confidence threshold
    pub confidence_threshold: f64,
}

/// Analytics complexity level
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum AnalyticsLevel {
    /// Basic analytics (low resource usage)
    Basic,
    /// Advanced analytics with ML features
    Advanced,
    /// Expert level with custom models
    Expert,
}

impl Default for DashboardConfig {
    fn default() -> Self {
        Self {
            network: Network::Bitcoin,
            analytics_level: AnalyticsLevel::Basic,
            database_url: "postgres://localhost/dash33".to_string(),
            api_config: ApiConfig {
                host: "127.0.0.1".to_string(),
                port: 3000,
                cors_enabled: true,
                rate_limit: RateLimit {
                    requests_per_second: 10,
                    burst_size: 50,
                },
            },
            ml_config: MLConfig {
                model_type: "lstm".to_string(),
                training_interval: 3600,
                confidence_threshold: 0.8,
            },
        }
    }
}

/// Application state shared across handlers
#[derive(Clone)]
pub struct AppState {
    /// Database connection pool
    pub pool: PgPool,
    /// Dashboard configuration
    pub config: DashboardConfig,
}

/// System metrics
#[derive(Debug, Clone, Serialize)]
pub struct Metrics {
    /// Number of transactions processed
    pub transactions: i64,
    /// Number of active users
    pub active_users: i64,
    /// System health score (0-1)
    pub system_health: f64,
    /// ML model accuracy
    pub model_accuracy: f64,
    /// API response time (ms)
    pub api_latency: f64,
}

/// Metric update request
#[derive(Debug, Clone, Deserialize)]
pub struct MetricUpdate {
    /// Type of metric to update
    pub metric_type: String,
    /// New value for the metric
    pub value: f64,
    /// Update timestamp
    pub timestamp: Option<chrono::DateTime<chrono::Utc>>,
}

/// Initialize the dashboard with given configuration
pub fn init(config: DashboardConfig) -> Result<Dashboard, Box<dyn std::error::Error>> {
    debug!("Initializing dashboard with config: {:?}", config);
    
    let dashboard = Dashboard::new(config)?;
    info!("Dashboard initialized successfully");
    
    Ok(dashboard)
}

/// Main dashboard struct
#[derive(Clone)]
pub struct Dashboard {
    config: DashboardConfig,
    state: Arc<AppState>,
}

impl Dashboard {
    /// Create a new dashboard instance
    pub fn new(config: DashboardConfig) -> Result<Self, Box<dyn std::error::Error>> {
        let pool = PgPool::connect(&config.database_url).await?;
        let state = Arc::new(AppState { pool, config: config.clone() });
        
        Ok(Self { config, state })
    }
    
    /// Start the dashboard server
    pub async fn run(&self) -> Result<(), Box<dyn std::error::Error>> {
        let router = self.create_router().await;
        let addr = format!("{}:{}", self.config.api_config.host, self.config.api_config.port);
        
        info!("Starting dashboard server on {}", addr);
        axum::Server::bind(&addr.parse()?)
            .serve(router.into_make_service())
            .await?;
            
        Ok(())
    }
    
    /// Create the API router
    async fn create_router(&self) -> Router {
        let cors = if self.config.api_config.cors_enabled {
            CorsLayer::new()
                .allow_origin(Any)
                .allow_methods(Any)
                .allow_headers(Any)
        } else {
            CorsLayer::new()
        };

        Router::new()
            .route("/metrics", get(get_metrics))
            .route("/metrics/update", post(update_metrics))
            .layer(cors)
            .with_state(self.state.clone())
    }
}

/// Get current system metrics
async fn get_metrics(State(state): State<Arc<AppState>>) -> Json<Metrics> {
    debug!("Fetching metrics");
    
    let metrics = Metrics {
        transactions: 100, // TODO: Implement real metrics
        active_users: 50,
        system_health: 0.99,
        model_accuracy: 0.95,
        api_latency: 50.0,
    };
    
    info!("Metrics retrieved successfully");
    Json(metrics)
}

/// Update system metrics
async fn update_metrics(
    State(state): State<Arc<AppState>>,
    Json(update): Json<MetricUpdate>,
) -> Json<bool> {
    debug!("Updating metric: {}", update.metric_type);
    
    // TODO: Implement real metric updates
    if update.value < 0.0 {
        warn!("Received negative metric value: {}", update.value);
    }
    
    info!("Metric updated successfully");
    Json(true)
}

#[cfg(test)]
mod tests {
    use super::*;
    use axum::http::StatusCode;
    use tower::ServiceExt;
    
    #[tokio::test]
    async fn test_dashboard_init() {
        let config = DashboardConfig::default();
        let result = init(config);
        assert!(result.is_ok());
    }
    
    #[tokio::test]
    async fn test_metrics_endpoint() {
        let config = DashboardConfig::default();
        let dashboard = init(config).unwrap();
        let router = dashboard.create_router().await;
        
        let response = router
            .oneshot(
                axum::http::Request::builder()
                    .uri("/metrics")
                    .body(axum::body::Body::empty())
                    .unwrap(),
            )
            .await
            .unwrap();
            
        assert_eq!(response.status(), StatusCode::OK);
    }
    
    #[tokio::test]
    async fn test_metric_update() {
        let config = DashboardConfig::default();
        let dashboard = init(config).unwrap();
        let router = dashboard.create_router().await;
        
        let update = MetricUpdate {
            metric_type: "system_health".to_string(),
            value: 0.98,
            timestamp: Some(chrono::Utc::now()),
        };
        
        let response = router
            .oneshot(
                axum::http::Request::builder()
                    .method("POST")
                    .uri("/metrics/update")
                    .header("content-type", "application/json")
                    .body(axum::body::Body::from(serde_json::to_string(&update).unwrap()))
                    .unwrap(),
            )
            .await
            .unwrap();
            
        assert_eq!(response.status(), StatusCode::OK);
    }
}
