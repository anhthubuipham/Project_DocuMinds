import javafx.application.Application;
import javafx.stage.Stage;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.VBox;
import javafx.stage.FileChooser;

import java.io.*;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.file.Files;
import java.util.HashMap;
import java.util.Map;

import com.google.gson.Gson;

public class Main extends Application {

    private TextArea documentArea = new TextArea();
    private Label resultLabel = new Label("Prediction: ");
    private File selectedFile;
    private String predictedCategory = "";
    private final Gson gson = new Gson();

    @Override
    public void start(Stage stage) {
        Button chooseFile = new Button("Choose Document");
        Button sendToAI = new Button("Classify with AI");
        Button sendFeedback = new Button("Send Feedback");

        chooseFile.setOnAction(e -> openFile(stage));
        sendToAI.setOnAction(e -> classifyDocument());
        sendFeedback.setOnAction(e -> sendFeedback());

        VBox layout = new VBox(10, chooseFile, documentArea, sendToAI, resultLabel, sendFeedback);
        layout.setStyle("-fx-padding: 20;");
        Scene scene = new Scene(layout, 600, 500);

        stage.setTitle("DocuMinds GUI");
        stage.setScene(scene);
        stage.show();
    }

    private void openFile(Stage stage) {
        FileChooser chooser = new FileChooser();
        chooser.getExtensionFilters().addAll(
            new FileChooser.ExtensionFilter("Text & PDF & DOCX", "*.txt", "*.pdf", "*.docx")
        );
        File file = chooser.showOpenDialog(stage);
        if (file != null) {
            selectedFile = file;
            try {
                String content = Files.readString(file.toPath());
                documentArea.setText(content);
            } catch (IOException ex) {
                documentArea.setText("Failed to read file: " + ex.getMessage());
            }
        }
    }

    private void classifyDocument() {
        if (selectedFile == null || documentArea.getText().isEmpty()) {
            resultLabel.setText("No file or empty text.");
            return;
        }

        Map<String, String> payload = new HashMap<>();
        payload.put("filename", selectedFile.getName());
        payload.put("text", documentArea.getText());

        try {
            String json = gson.toJson(payload);
            HttpRequest request = HttpRequest.newBuilder()
                .uri(new URI("http://localhost:5000/classify"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(json))
                .build();

            HttpResponse<String> response = HttpClient.newHttpClient().send(request, HttpResponse.BodyHandlers.ofString());
            Map<String, String> result = gson.fromJson(response.body(), Map.class);
            predictedCategory = result.get("predicted_category");
            resultLabel.setText("Prediction: " + predictedCategory);
        } catch (Exception e) {
            resultLabel.setText("Error: " + e.getMessage());
        }
    }

    private void sendFeedback() {
        if (predictedCategory.isEmpty()) {
            resultLabel.setText("Run classification first.");
            return;
        }

        TextInputDialog dialog = new TextInputDialog(predictedCategory);
        dialog.setTitle("Feedback");
        dialog.setHeaderText("Correct the category if needed");
        dialog.setContentText("Correct category:");

        dialog.showAndWait().ifPresent(correctCategory -> {
            Map<String, String> payload = new HashMap<>();
            payload.put("filename", selectedFile.getName());
            payload.put("predicted_category", predictedCategory);
            payload.put("correct_category", correctCategory);
            payload.put("text_excerpt", documentArea.getText().substring(0, Math.min(150, documentArea.getText().length())));

            try {
                String json = gson.toJson(payload);
                HttpRequest request = HttpRequest.newBuilder()
                    .uri(new URI("http://localhost:5000/feedback"))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(json))
                    .build();

                HttpClient.newHttpClient().send(request, HttpResponse.BodyHandlers.ofString());
                resultLabel.setText("✅ Feedback sent!");
            } catch (Exception e) {
                resultLabel.setText("Feedback error: " + e.getMessage());
            }
        });
    }

    public static void main(String[] args) {
        launch();
    }
}
