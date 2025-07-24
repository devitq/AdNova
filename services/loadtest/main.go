package main

import (
	"bytes"
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"html/template"
	"io"
	"log"
	"math/rand"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"

	"github.com/gorilla/mux"
	"github.com/gorilla/websocket"
)

// --- Mock Data Structures ---

type Client struct {
	ClientID string `json:"client_id"`
	Login    string `json:"login"`
	Age      int    `json:"age"`
	Location string `json:"location"`
	Gender   string `json:"gender"`
}

type Advertiser struct {
	AdvertiserID string `json:"advertiser_id"`
	Name         string `json:"name"`
}

type MLScore struct {
	AdvertiserId string `json:"advertiser_id"`
	ClientID     string `json:"client_id"`
	Score        int64  `json:"score"`
}

type Campaign struct {
	Targeting struct {
		Gender   string `json:"gender,omitempty"`
		AgeFrom  int    `json:"age_from,omitempty"`
		AgeTo    int    `json:"age_to,omitempty"`
		Location string `json:"location,omitempty"`
	} `json:"targeting"`
	AdTitle           string  `json:"ad_title"`
	AdText            string  `json:"ad_text"`
	ImpressionsLimit  int     `json:"impressions_limit"`
	ClicksLimit       int     `json:"clicks_limit"`
	CostPerImpression float64 `json:"cost_per_impression"`
	CostPerClick      float64 `json:"cost_per_click"`
	StartDate         int64   `json:"start_date"`
	EndDate           int64   `json:"end_date"`
}

type CampaignFileEntry struct {
	AdvertiserID string   `json:"advertiser_id"`
	CampaignData Campaign `json:"campaign_data"`
}

// --- Mock data filenames ---

const clientsMockDataFile = "./mocks/bulk_clients.json"
const advertisersMockDataFile = "./mocks/bulk_advertisers.json"
const campaignsMockDataFile = "./mocks/campaigns.json"
const mlscoresMockDataFile = "./mocks/ml_scores.json"

// --- In-Memory Data Store ---

var (
	loadedClientIDs []string
	dataMutex       = &sync.RWMutex{}
	backendAddress  string
)

// --- Mock Data Loading and Posting Logic ---

func loadInitialMockIDs() {
	dataMutex.Lock()
	defer dataMutex.Unlock()

	loadedClientIDs = nil

	log.Println("Loading client IDs from local files...")

	readFile := func(filename string) ([]byte, error) {
		content, err := os.ReadFile(filename)
		if err != nil {
			return nil, fmt.Errorf("error reading %s: %w", filename, err)
		}
		return content, nil
	}

	clientsContent, err := readFile(clientsMockDataFile)
	if err != nil {
		log.Printf("Warning: Could not read %s for initial ID load: %v", clientsMockDataFile, err)
	} else {
		var tempClients []Client
		if err := json.Unmarshal(clientsContent, &tempClients); err != nil {
			log.Printf("Warning: Error unmarshaling %s for initial ID load: %v", clientsMockDataFile, err)
		} else {
			for _, c := range tempClients {
				loadedClientIDs = append(loadedClientIDs, c.ClientID)
			}
			log.Printf("Loaded %d client IDs for stress testing.", len(loadedClientIDs))
		}
	}
}

func loadAndPostMocks() error {
	log.Println("Attempting to load mock data from files and post to external backend:", backendAddress)

	readFile := func(filename string) ([]byte, error) {
		content, err := os.ReadFile(filename)
		if err != nil {
			return nil, fmt.Errorf("error reading %s: %w", filename, err)
		}
		return content, nil
	}

	postJSON := func(url string, data interface{}) error {
		jsonData, err := json.Marshal(data)
		if err != nil {
			return fmt.Errorf("failed to marshal JSON for %s: %w", url, err)
		}
		req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
		if err != nil {
			return fmt.Errorf("failed to create request for %s: %w", url, err)
		}
		req.Header.Set("Content-Type", "application/json")

		client := &http.Client{
			Timeout: 60 * time.Second,
		}

		resp, err := client.Do(req)
		if err != nil {
			return fmt.Errorf("failed to POST to %s: %w", url, err)
		}
		defer resp.Body.Close()

		if resp.StatusCode >= 400 {
			body, _ := io.ReadAll(resp.Body)
			return fmt.Errorf("POST to %s failed with status %d: %s", url, resp.StatusCode, string(body))
		}
		return nil
	}

	// 1. Load bulk_clients.json
	clientsContent, err := readFile(clientsMockDataFile)
	if err != nil {
		return err
	}
	var tempClients []Client
	if err := json.Unmarshal(clientsContent, &tempClients); err != nil {
		return fmt.Errorf("error unmarshaling %s: %w", clientsMockDataFile, err)
	}
	if err := postJSON(fmt.Sprintf("%s/clients/bulk", backendAddress), tempClients); err != nil {
		return fmt.Errorf("error posting bulk clients: %w", err)
	}
	log.Printf("Successfully posted %d clients to %s/clients/bulk", len(tempClients), backendAddress)

	// 2. Load bulk_advertisers.json
	advertisersContent, err := readFile(advertisersMockDataFile)
	if err != nil {
		return err
	}
	var tempAdvertisers []Advertiser
	if err := json.Unmarshal(advertisersContent, &tempAdvertisers); err != nil {
		return fmt.Errorf("error unmarshaling %s: %w", advertisersMockDataFile, err)
	}
	if err := postJSON(fmt.Sprintf("%s/advertisers/bulk", backendAddress), tempAdvertisers); err != nil {
		return fmt.Errorf("error posting bulk advertisers: %w", err)
	}
	log.Printf("Successfully posted %d advertisers to %s/advertisers/bulk", len(tempAdvertisers), backendAddress)

	// 3. Load campaigns.json
	campaignsContent, err := readFile(campaignsMockDataFile)
	if err != nil {
		return err
	}
	var campaignDataList []CampaignFileEntry
	if err := json.Unmarshal(campaignsContent, &campaignDataList); err != nil {
		return fmt.Errorf("error unmarshaling %s: %w", campaignsMockDataFile, err)
	}

	for i, entry := range campaignDataList {
		if err := postJSON(fmt.Sprintf("%s/advertisers/%s/campaigns", backendAddress, entry.AdvertiserID), entry.CampaignData); err != nil {
			log.Printf("Warning: Failed to post campaign for advertiser %s (entry %d): %v", entry.AdvertiserID, i, err)
		}
	}
	log.Printf("Attempted to post campaigns for %d advertisers from %s", len(campaignDataList), campaignsMockDataFile)

	// 4. Load ml_scores.json
	mlScoresContent, err := readFile(mlscoresMockDataFile)
	if err != nil {
		return err
	}
	var tempMLScores []MLScore
	if err := json.Unmarshal(mlScoresContent, &tempMLScores); err != nil {
		return fmt.Errorf("error unmarshaling %s: %w", mlscoresMockDataFile, err)
	}
	for i, score := range tempMLScores {
		if err := postJSON(fmt.Sprintf("%s/ml-scores", backendAddress), score); err != nil {
			log.Printf("Warning: Failed to post ML score %d (client %s): %v", i, score.ClientID, err)
		}
	}
	log.Printf("Attempted to post %d ML scores one by one to %s/ml-scores", len(tempMLScores), backendAddress)

	log.Println("Mock data loading and posting process complete.")
	return nil
}

// --- WebSocket Hub ---

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin:     func(r *http.Request) bool { return true },
}

type Hub struct {
	clients    map[*websocket.Conn]bool
	broadcast  chan []byte
	register   chan *websocket.Conn
	unregister chan *websocket.Conn
	mutex      sync.Mutex
}

func newHub() *Hub {
	return &Hub{
		broadcast:  make(chan []byte),
		register:   make(chan *websocket.Conn),
		unregister: make(chan *websocket.Conn),
		clients:    make(map[*websocket.Conn]bool),
	}
}

func (h *Hub) run() {
	for {
		select {
		case client := <-h.register:
			h.mutex.Lock()
			h.clients[client] = true
			h.mutex.Unlock()
		case client := <-h.unregister:
			h.mutex.Lock()
			if _, ok := h.clients[client]; ok {
				delete(h.clients, client)
				client.Close()
			}
			h.mutex.Unlock()
		case message := <-h.broadcast:
			h.mutex.Lock()
			for client := range h.clients {
				err := client.WriteMessage(websocket.TextMessage, message)
				if err != nil {
					log.Printf("error: %v", err)
					client.Close()
					delete(h.clients, client)
				}
			}
			h.mutex.Unlock()
		}
	}
}

var hub = newHub()

// --- Load Generator ---

type TestConfig struct {
	BackendAddress string `json:"backendAddress"`
	MaxRPS         int    `json:"maxRps"`
	LoadProfile    string `json:"loadProfile"`
	FromRPS        int    `json:"fromRPS"`
	ToRPS          int    `json:"toRPS"`
	StepRPS        int    `json:"stepRps"`
	StepDuration   int    `json:"stepDuration"`
	OnceCount      int    `json:"onceCount"`
}

type RequestResult struct {
	StatusCode int
	Latency    time.Duration
	Error      bool
}

type TestStats struct {
	RPS         int     `json:"rps"`
	Latency     float64 `json:"latency"`
	ErrorRate   float64 `json:"errorRate"`
	TotalReqs   int64   `json:"totalReqs"`
	TotalErrors int64   `json:"totalErrors"`
	IsRunning   bool    `json:"isRunning"`
}

type TestManager struct {
	config     TestConfig
	isRunning  bool
	cancelFunc context.CancelFunc
	mutex      sync.Mutex
	httpClient *http.Client
}

var testManager = TestManager{
	httpClient: &http.Client{
		Timeout: 10 * time.Second,
		Transport: &http.Transport{
			MaxIdleConns:        1000,
			MaxIdleConnsPerHost: 1000,
			IdleConnTimeout:     90 * time.Second,
		},
	},
}

func (tm *TestManager) startTest(config TestConfig) {
	tm.mutex.Lock()
	if tm.isRunning {
		tm.mutex.Unlock()
		log.Println("Test already running.")
		return
	}

	tm.config = config
	tm.isRunning = true
	ctx, cancel := context.WithCancel(context.Background())
	tm.cancelFunc = cancel
	tm.mutex.Unlock()

	go tm.runLoadGenerator(ctx)
}

func (tm *TestManager) stopTest() {
	tm.mutex.Lock()
	if tm.isRunning && tm.cancelFunc != nil {
		tm.cancelFunc()
		tm.isRunning = false
	}
	tm.mutex.Unlock()
}

func (tm *TestManager) runLoadGenerator(ctx context.Context) {
	log.Printf("Starting test with config: %+v\n", tm.config)

	results := make(chan RequestResult, 10000)
	var wg sync.WaitGroup

	var totalReqs, totalErrors int64
	go func() {
		ticker := time.NewTicker(1 * time.Second)
		defer ticker.Stop()
		var reqsInSecond int
		var totalLatency time.Duration
		var errorsInSecond int

		for {
			select {
			case <-ctx.Done():
				return
			case <-ticker.C:
				avgLatency := 0.0
				if reqsInSecond > 0 {
					avgLatency = float64(totalLatency.Milliseconds()) / float64(reqsInSecond)
				}
				errorRate := 0.0
				if reqsInSecond > 0 {
					errorRate = float64(errorsInSecond) / float64(reqsInSecond) * 100
				}

				stats := TestStats{
					RPS:         reqsInSecond,
					Latency:     avgLatency,
					ErrorRate:   errorRate,
					TotalReqs:   totalReqs,
					TotalErrors: totalErrors,
					IsRunning:   true,
				}
				jsonStats, _ := json.Marshal(stats)
				hub.broadcast <- jsonStats

				reqsInSecond = 0
				totalLatency = 0
				errorsInSecond = 0
			case res, ok := <-results:
				if !ok {
					return
				}
				totalReqs++
				reqsInSecond++
				totalLatency += res.Latency
				if res.Error {
					totalErrors++
					errorsInSecond++
				}
			}
		}
	}()

	numWorkers := 1000
	if tm.config.MaxRPS > 0 && tm.config.MaxRPS < numWorkers {
		numWorkers = tm.config.MaxRPS
	}

	jobs := make(chan string, 10000)

	for i := 0; i < numWorkers; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for {
				select {
				case <-ctx.Done():
					return
				case url, ok := <-jobs:
					if !ok {
						return
					}
					start := time.Now()
					req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
					resp, err := tm.httpClient.Do(req)
					latency := time.Since(start)

					if err != nil {
						results <- RequestResult{StatusCode: 0, Latency: latency, Error: true}
						continue
					}

					results <- RequestResult{StatusCode: resp.StatusCode, Latency: latency, Error: resp.StatusCode >= 500}
					resp.Body.Close()
				}
			}
		}()
	}

	go func() {
		defer close(jobs)

		dataMutex.RLock()
		if len(loadedClientIDs) == 0 {
			log.Println("No client IDs loaded for stress test.")
			dataMutex.RUnlock()
			return
		}
		clientIDsForTest := make([]string, len(loadedClientIDs))
		copy(clientIDsForTest, loadedClientIDs)
		dataMutex.RUnlock()

		log.Printf("Stress testing with %d client IDs.", len(clientIDsForTest))

		switch tm.config.LoadProfile {
		case "const":
			ticker := time.NewTicker(time.Second / time.Duration(tm.config.MaxRPS))
			defer ticker.Stop()
			for {
				select {
				case <-ctx.Done():
					return
				case <-ticker.C:
					clientID := clientIDsForTest[rand.Intn(len(clientIDsForTest))]
					url := fmt.Sprintf("%s/ads?client_id=%s", tm.config.BackendAddress, clientID)
					jobs <- url
				}
			}
		case "line":
			duration := 10 * time.Second
			startTime := time.Now()
			for {
				select {
				case <-ctx.Done():
					return
				default:
					elapsed := time.Since(startTime)
					if elapsed >= duration {
						elapsed = duration
					}

					progress := float64(elapsed) / float64(duration)
					currentRPS := float64(tm.config.FromRPS) + (float64(tm.config.ToRPS-tm.config.FromRPS) * progress)

					if currentRPS <= 0 {
						currentRPS = 1
					}

					sleepDuration := time.Second / time.Duration(currentRPS)
					time.Sleep(sleepDuration)

					clientID := clientIDsForTest[rand.Intn(len(clientIDsForTest))]
					url := fmt.Sprintf("%s/ads?client_id=%s", tm.config.BackendAddress, clientID)
					jobs <- url

					if elapsed >= duration {
						constSleepDuration := time.Second / time.Duration(tm.config.ToRPS)
						for {
							select {
							case <-ctx.Done():
								return
							default:
								time.Sleep(constSleepDuration)
								clientID := clientIDsForTest[rand.Intn(len(clientIDsForTest))]
								url := fmt.Sprintf("%s/ads?client_id=%s", tm.config.BackendAddress, clientID)
								jobs <- url
							}
						}
					}
				}
			}
		case "step":
			currentRPS := tm.config.FromRPS
			for currentRPS <= tm.config.ToRPS {
				log.Printf("Step load: %d RPS for %d seconds", currentRPS, tm.config.StepDuration)
				stepEndTime := time.After(time.Duration(tm.config.StepDuration) * time.Second)

				sleepDuration := time.Second / time.Duration(currentRPS)

			stepLoop:
				for {
					select {
					case <-ctx.Done():
						return
					case <-stepEndTime:
						break stepLoop
					default:
						time.Sleep(sleepDuration)
						clientID := clientIDsForTest[rand.Intn(len(clientIDsForTest))]
						url := fmt.Sprintf("%s/ads?client_id=%s", tm.config.BackendAddress, clientID)
						jobs <- url
					}
				}
				currentRPS += tm.config.StepRPS
				if tm.config.StepRPS == 0 && currentRPS != tm.config.ToRPS {
					break
				}
			}
		case "once":
			for i := 0; i < tm.config.OnceCount; i++ {
				select {
				case <-ctx.Done():
					return
				default:
					clientID := clientIDsForTest[rand.Intn(len(clientIDsForTest))]
					url := fmt.Sprintf("%s/ads?client_id=%s", tm.config.BackendAddress, clientID)
					jobs <- url
				}
			}
		case "unlimited":
			for {
				select {
				case <-ctx.Done():
					return
				default:
					clientID := clientIDsForTest[rand.Intn(len(clientIDsForTest))]
					url := fmt.Sprintf("%s/ads?client_id=%s", tm.config.BackendAddress, clientID)
					jobs <- url
				}
			}
		}
	}()

	wg.Wait()
	close(results)
	time.Sleep(1 * time.Second)

	tm.mutex.Lock()
	tm.isRunning = false
	tm.mutex.Unlock()

	finalStats := TestStats{IsRunning: false, TotalReqs: totalReqs, TotalErrors: totalErrors}
	jsonStats, _ := json.Marshal(finalStats)
	hub.broadcast <- jsonStats
	log.Println("Test finished.")
}

// --- HTTP Handlers ---

func serveWs(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println(err)
		return
	}
	hub.register <- conn

	go func() {
		defer func() {
			hub.unregister <- conn
			conn.Close()
		}()
		for {
			if _, _, err := conn.NextReader(); err != nil {
				break
			}
		}
	}()
}

func handleLoadMocks(w http.ResponseWriter, r *http.Request) {
	if err := loadAndPostMocks(); err != nil {
		http.Error(w, fmt.Sprintf("Failed to load mocks: %v", err), http.StatusInternalServerError)
		return
	}
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"status": "Mocks loaded successfully"})
}

func checkEndpoint(url string) bool {
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		log.Printf("Error creating request for %s: %v", url, err)
		return false
	}
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	req = req.WithContext(ctx)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		log.Printf("Error making request to %s: %v", url, err)
		return false
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		log.Printf("Check for %s failed with status: %d", url, resp.StatusCode)
		return false
	}

	if strings.Contains(url, "/campaigns") {
		bodyBytes, err := io.ReadAll(resp.Body)
		if err != nil {
			log.Printf("Error reading response body from %s: %v", url, err)
			return false
		}
		var campaignsData []Campaign
		if err := json.Unmarshal(bodyBytes, &campaignsData); err != nil {
			log.Printf("Error unmarshaling campaign data from %s: %v", url, err)
			return false
		}
		return len(campaignsData) > 0
	}
	return true
}

func handleCheckMocks(w http.ResponseWriter, r *http.Request) {
	dataMutex.RLock()
	defer dataMutex.RUnlock()

	status := make(map[string]bool)

	var tempClients []Client
	clientsContent, err := os.ReadFile(clientsMockDataFile)
	if err != nil {
		log.Printf("Warning: Could not read %s for checks: %v", clientsMockDataFile, err)
	} else {
		json.Unmarshal(clientsContent, &tempClients)
	}

	var tempAdvertisers []Advertiser
	advertisersContent, err := os.ReadFile(advertisersMockDataFile)
	if err != nil {
		log.Printf("Warning: Could not read %s for checks: %v", advertisersMockDataFile, err)
	} else {
		json.Unmarshal(advertisersContent, &tempAdvertisers)
	}

	clientsLoaded := false
	if len(tempClients) >= 3 {
		firstClient := tempClients[0].ClientID
		medianClient := tempClients[len(tempClients)/2].ClientID
		lastClient := tempClients[len(tempClients)-1].ClientID

		clientsLoaded = checkEndpoint(fmt.Sprintf("%s/clients/%s", backendAddress, firstClient)) &&
			checkEndpoint(fmt.Sprintf("%s/clients/%s", backendAddress, medianClient)) &&
			checkEndpoint(fmt.Sprintf("%s/clients/%s", backendAddress, lastClient))
	} else if len(tempClients) > 0 {
		clientsLoaded = checkEndpoint(fmt.Sprintf("%s/clients/%s", backendAddress, tempClients[0].ClientID))
	}
	status["clients"] = clientsLoaded

	advertisersLoaded := false
	if len(tempAdvertisers) >= 3 {
		firstAdvertiser := tempAdvertisers[0].AdvertiserID
		medianAdvertiser := tempAdvertisers[len(tempAdvertisers)/2].AdvertiserID
		lastAdvertiser := tempAdvertisers[len(tempAdvertisers)-1].AdvertiserID

		advertisersLoaded = checkEndpoint(fmt.Sprintf("%s/advertisers/%s", backendAddress, firstAdvertiser)) &&
			checkEndpoint(fmt.Sprintf("%s/advertisers/%s", backendAddress, medianAdvertiser)) &&
			checkEndpoint(fmt.Sprintf("%s/advertisers/%s", backendAddress, lastAdvertiser))
	} else if len(tempAdvertisers) > 0 {
		advertisersLoaded = checkEndpoint(fmt.Sprintf("%s/advertisers/%s", backendAddress, tempAdvertisers[0].AdvertiserID))
	}
	status["advertisers"] = advertisersLoaded

	campaignsLoaded := false
	if len(tempAdvertisers) >= 3 {
		firstAdvertiser := tempAdvertisers[0].AdvertiserID
		medianAdvertiser := tempAdvertisers[len(tempAdvertisers)/2].AdvertiserID
		lastAdvertiser := tempAdvertisers[len(tempAdvertisers)-1].AdvertiserID

		campaignsLoaded = checkEndpoint(fmt.Sprintf("%s/advertisers/%s/campaigns", backendAddress, firstAdvertiser)) &&
			checkEndpoint(fmt.Sprintf("%s/advertisers/%s/campaigns", backendAddress, medianAdvertiser)) &&
			checkEndpoint(fmt.Sprintf("%s/advertisers/%s/campaigns", backendAddress, lastAdvertiser))
	} else if len(tempAdvertisers) > 0 {
		campaignsLoaded = checkEndpoint(fmt.Sprintf("%s/advertisers/%s/campaigns", backendAddress, tempAdvertisers[0].AdvertiserID))
	}
	status["campaigns"] = campaignsLoaded

	_, err = os.ReadFile(mlscoresMockDataFile)
	status["ml_scores"] = err == nil
	if !status["ml_scores"] {
		log.Printf("Warning: ML Scores file not found or readable, assuming not loaded for check.")
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(status)
}

func handleStartTest(w http.ResponseWriter, r *http.Request) {
	var config TestConfig
	if err := json.NewDecoder(r.Body).Decode(&config); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	config.BackendAddress = backendAddress
	go testManager.startTest(config)
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"status": "Test started"})
}

func handleStopTest(w http.ResponseWriter, r *http.Request) {
	testManager.stopTest()
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"status": "Test stopped"})
}

func main() {
	rand.Seed(time.Now().UnixNano())

	port := flag.String("port", "5002", "Port to run the server on")
	flag.Parse()

	backendAddress = os.Getenv("BACKEND_ADDRESS")
	if backendAddress == "" {
		log.Println("BACKEND_ADDRESS environment variable not set. Defaulting to http://localhost:8080")
		backendAddress = "http://localhost:8080"
	}

	loadInitialMockIDs()

	go hub.run()

	r := mux.NewRouter()

	r.HandleFunc("/", serveUI)
	r.HandleFunc("/ws", serveWs)
	r.HandleFunc("/api/load-mocks", handleLoadMocks).Methods("POST")
	r.HandleFunc("/api/check-mocks", handleCheckMocks).Methods("GET")
	r.HandleFunc("/api/start-test", handleStartTest).Methods("POST")
	r.HandleFunc("/api/stop-test", handleStopTest).Methods("POST")

	addr := ":" + *port
	log.Printf("Server starting on port %s. Open http://localhost%s\n", *port, addr)
	if err := http.ListenAndServe(addr, r); err != nil {
		log.Fatal("ListenAndServe: ", err)
	}
}

// --- Embedded HTML UI ---

func serveUI(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/html; charset=utf-8")

	t, err := template.ParseFiles("static/index.html")
	if err != nil {
		http.Error(w, "Could not load UI template", http.StatusInternalServerError)
		return
	}

	err = t.Execute(w, nil)
	if err != nil {
		http.Error(w, "Failed to render UI", http.StatusInternalServerError)
	}
}
