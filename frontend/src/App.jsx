import { useEffect, useRef, useState } from "react";
import "./App.css";

import * as pdfjsLib from "pdfjs-dist";
import Tesseract from "tesseract.js";
import pdfWorker from "pdfjs-dist/build/pdf.worker.min.mjs?url";

pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorker;

const API_URL = "http://127.0.0.1:5000/api/agent/chat";
const DOCUMENT_API_URL = "http://127.0.0.1:5000/api/analyze";

const languages = [
  "English",
  "Telugu",
  "Hindi",
  "Malayalam",
  "Tamil",
  "Kannada",
];

const speechLanguages = {
  English: "en-IN",
  Telugu: "te-IN",
  Hindi: "hi-IN",
  Malayalam: "ml-IN",
  Tamil: "ta-IN",
  Kannada: "kn-IN",
};

const quickActions = [
  {
    title: "Analyze Report",
    icon: "📄",
    message:
      "Analyze my medical report and explain the important findings.",
  },
  {
    title: "Medicine Information",
    icon: "💊",
    message:
      "Give me information about my medicines and important safety points.",
  },
  {
    title: "Health Trends",
    icon: "📊",
    message:
      "Analyze my health trends and explain what has changed.",
  },
  {
    title: "Doctor Visit",
    icon: "🩺",
    message:
      "Prepare a summary of the important things I should discuss with my doctor.",
  },
  {
    title: "Safety Check",
    icon: "🛡️",
    message:
      "Perform a safety check based on my health information.",
  },
];

function App() {
  const [activePage, setActivePage] = useState("dashboard");

  const [language, setLanguage] = useState("English");
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const [workflow, setWorkflow] = useState([]);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isListening, setIsListening] = useState(false);

  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");

  // =========================================================
  // REPORT MEMORY
  // Stores the latest analyzed report so MediSaathi
  // can answer follow-up questions about it.
  // =========================================================

  const [reportContext, setReportContext] = useState(null);

  const fileInputRef = useRef(null);
  const recognitionRef = useRef(null);
  const speechVoicesRef = useRef([]);

  // =========================================================
  // SPEECH VOICES
  // =========================================================

  useEffect(() => {
    const loadVoices = () => {
      speechVoicesRef.current =
        window.speechSynthesis?.getVoices() || [];
    };

    loadVoices();

    if (window.speechSynthesis) {
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }

    return () => {
      if (window.speechSynthesis) {
        window.speechSynthesis.onvoiceschanged = null;
      }
    };
  }, []);

  // =========================================================
  // VOICE
  // =========================================================

  const getBestVoice = (languageName) => {
    const voices = speechVoicesRef.current || [];
    const target = speechLanguages[languageName] || "en-IN";

    if (!voices.length) return null;

    const exact = voices.find(
      (voice) =>
        voice.lang?.toLowerCase() === target.toLowerCase()
    );

    if (exact) return exact;

    const prefix = target.split("-")[0].toLowerCase();

    return (
      voices.find((voice) =>
        voice.lang?.toLowerCase().startsWith(prefix)
      ) ||
      voices[0] ||
      null
    );
  };

  const speakResponse = (text) => {
    if (!text || !window.speechSynthesis) return;

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);

    utterance.lang =
      speechLanguages[language] || "en-IN";

    const voice = getBestVoice(language);

    if (voice) {
      utterance.voice = voice;
    }

    utterance.rate = 0.95;
    utterance.pitch = 1;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utterance);
  };

  const stopSpeaking = () => {
    window.speechSynthesis?.cancel();
    setIsSpeaking(false);
  };

  // =========================================================
  // VOICE INPUT
  // =========================================================

  const startListening = () => {
    const SpeechRecognition =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert(
        "Voice input is not supported in this browser. Please use Chrome."
      );
      return;
    }

    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
      return;
    }

    const recognition = new SpeechRecognition();

    recognition.lang =
      speechLanguages[language] || "en-IN";

    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => setIsListening(true);

    recognition.onresult = (event) => {
      const transcript =
        event.results?.[0]?.[0]?.transcript || "";

      if (transcript) {
        setMessage(transcript);
      }
    };

    recognition.onerror = (event) => {
      console.error(
        "Speech recognition error:",
        event.error
      );
      setIsListening(false);
    };

    recognition.onend = () => setIsListening(false);

    recognitionRef.current = recognition;
    recognition.start();
  };

  // =========================================================
  // WORKFLOW
  // =========================================================

  const updateWorkflow = (steps) => {
    setWorkflow(Array.isArray(steps) ? steps : []);
  };

  // =========================================================
  // CHAT
  // =========================================================

  const sendMessage = async (text = message) => {
    const cleanMessage = String(text || "").trim();

    if (!cleanMessage || loading) return;

    setMessage("");

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: cleanMessage,
      },
    ]);

    setLoading(true);

    updateWorkflow([
      {
        name: "Understanding request",
        status: "running",
      },
    ]);

    try {
      // =====================================================
      // REPORT CONTEXT
      // =====================================================

      let reportInformation = "";

      if (reportContext) {
        reportInformation = `

IMPORTANT MEDICAL REPORT CONTEXT

The user has uploaded and analyzed a medical report.

Use the report information below when answering the user's question.

--------------------------------------------------
ORIGINAL EXTRACTED REPORT TEXT
--------------------------------------------------

${reportContext.original_report_text || "No raw report text available."}

--------------------------------------------------
ANALYZED REPORT DATA
--------------------------------------------------

${JSON.stringify(reportContext, null, 2)}

--------------------------------------------------
REPORT INSTRUCTIONS
--------------------------------------------------

- Use the uploaded report information when relevant.
- Answer questions about values that are present in the report.
- Do not say that the report information is unavailable when it exists above.
- Preserve medical values, units, dates, names and dosages exactly.
- Clearly distinguish report facts from general explanation.
- Do not diagnose.
- Do not prescribe.
- Do not recommend changing medicines or treatment.
- If the user asks for medical decisions, advise discussion with a qualified healthcare professional.
`;
      }

      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: cleanMessage + reportInformation,

          language,

          patient_name: "Demo User",

          measurements:
            reportContext?.measurements ||
            reportContext?.clinical_analysis?.measurements ||
            {},

          health_history: reportContext
            ? [reportContext]
            : [],
        }),
      });

      const data = await response.json();

      console.log("CHAT BACKEND RESPONSE:", data);

      if (!response.ok || !data.success) {
        throw new Error(
          data.error ||
            data.message ||
            "Unable to get a response."
        );
      }

      let assistantResponse = data.response;

      if (
        assistantResponse &&
        typeof assistantResponse === "object"
      ) {
        assistantResponse =
          assistantResponse.response ||
          assistantResponse.message ||
          assistantResponse.final_summary ||
          JSON.stringify(assistantResponse);
      }

      assistantResponse = String(
        assistantResponse ||
          "I could not generate a response."
      ).trim();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: assistantResponse,
        },
      ]);

      updateWorkflow([
        {
          name: "Understanding request",
          status: "completed",
        },
        {
          name: "Generating response",
          status: "completed",
        },
      ]);

      speakResponse(assistantResponse);
    } catch (error) {
      console.error("Chat error:", error);

      const errorMessage =
        "I could not connect to the CareVault backend. Please make sure the backend is running.";

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: errorMessage,
        },
      ]);

      updateWorkflow([
        {
          name: "Backend connection",
          status: "failed",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // FILE UPLOAD
  // =========================================================

  const openFilePicker = () => {
    if (!loading && !uploading) {
      fileInputRef.current?.click();
    }
  };

  const handleFileSelected = async (event) => {
    const file = event.target.files?.[0];

    if (!file) return;

    await analyzeUploadedFile(file);

    event.target.value = "";
  };

  // =========================================================
  // PDF TEXT EXTRACTION
  // =========================================================

  const extractPdfText = async (file) => {
    const arrayBuffer = await file.arrayBuffer();

    const pdf = await pdfjsLib.getDocument({
      data: arrayBuffer,
    }).promise;

    let fullText = "";

    for (
      let pageNumber = 1;
      pageNumber <= pdf.numPages;
      pageNumber++
    ) {
      const page = await pdf.getPage(pageNumber);

      const textContent =
        await page.getTextContent();

      let lastY = null;
      let pageLines = [];
      let currentLine = "";

      for (const item of textContent.items) {
        if (!item.str && !item.hasEOL) continue;
        const currentY = item.transform ? item.transform[5] : null;

        if (
          lastY !== null &&
          currentY !== null &&
          Math.abs(currentY - lastY) > 5
        ) {
          if (currentLine.trim()) {
            pageLines.push(currentLine.trim());
          }
          currentLine = item.str || "";
        } else {
          if (
            currentLine &&
            item.str &&
            !currentLine.endsWith(" ") &&
            !item.str.startsWith(" ")
          ) {
            currentLine += " ";
          }
          currentLine += item.str || "";
        }

        if (item.hasEOL) {
          if (currentLine.trim()) {
            pageLines.push(currentLine.trim());
          }
          currentLine = "";
        }
        lastY = currentY;
      }

      if (currentLine.trim()) {
        pageLines.push(currentLine.trim());
      }

      fullText +=
        `\n\n--- Page ${pageNumber} ---\n\n` +
        pageLines.join("\n");
    }

    return {
      text: fullText.trim(),
      pdf,
    };
  };

  // =========================================================
  // IMAGE OCR
  // =========================================================

  const extractImageText = async (file) => {
    const result = await Tesseract.recognize(
      file,
      "eng",
      {
        logger: (info) => {
          if (
            info.status === "recognizing text"
          ) {
            const progress = Math.round(
              (info.progress || 0) * 100
            );

            setUploadStatus(
              `Reading report... ${progress}%`
            );
          }
        },
      }
    );

    return result.data.text || "";
  };

  // =========================================================
  // PDF OCR
  // =========================================================

  const ocrPdf = async (pdf) => {
    let fullText = "";

    for (
      let pageNumber = 1;
      pageNumber <= pdf.numPages;
      pageNumber++
    ) {
      setUploadStatus(
        `Scanning page ${pageNumber} of ${pdf.numPages}...`
      );

      const page =
        await pdf.getPage(pageNumber);

      const viewport =
        page.getViewport({
          scale: 2,
        });

      const canvas =
        document.createElement("canvas");

      const context =
        canvas.getContext("2d");

      canvas.width = viewport.width;
      canvas.height = viewport.height;

      await page.render({
        canvasContext: context,
        viewport,
      }).promise;

      const result =
        await Tesseract.recognize(
          canvas,
          "eng",
          {
            logger: (info) => {
              if (
                info.status ===
                "recognizing text"
              ) {
                const progress =
                  Math.round(
                    (info.progress || 0) * 100
                  );

                setUploadStatus(
                  `Reading page ${pageNumber}/${pdf.numPages}... ${progress}%`
                );
              }
            },
          }
        );

      fullText +=
        `\n\n--- Page ${pageNumber} ---\n\n` +
        (result.data.text || "");
    }

    return fullText.trim();
  };

  // =========================================================
  // DOCUMENT TEXT
  // =========================================================

  const extractDocumentText = async (file) => {
    const type = file.type;

    if (
      type === "image/png" ||
      type === "image/jpeg" ||
      type === "image/jpg"
    ) {
      setUploadStatus(
        "Reading medical report image..."
      );

      return (
        await extractImageText(file)
      ).trim();
    }

    if (
      type === "application/pdf" ||
      file.name
        .toLowerCase()
        .endsWith(".pdf")
    ) {
      setUploadStatus("Opening PDF...");

      const result =
        await extractPdfText(file);

      if (result.text.length >= 80) {
        return result.text;
      }

      setUploadStatus(
        "Scanned PDF detected. Starting OCR..."
      );

      return await ocrPdf(result.pdf);
    }

    throw new Error(
      "Please upload a PDF, PNG, JPG, or JPEG medical report."
    );
  };

  // =========================================================
  // SEND DOCUMENT TO BACKEND
  // =========================================================

  const analyzeDocumentWithBackend =
    async (documentText) => {
      const response = await fetch(
        DOCUMENT_API_URL,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            patient_name: "Demo User",
            document_text: documentText,
            target_language: language,
            measurements: {},
            health_history: [],
          }),
        }
      );

      const data = await response.json();

      console.log(
        "DOCUMENT BACKEND RESPONSE:",
        data
      );

      if (!response.ok || !data.success) {
        throw new Error(
          data.error ||
            data.message ||
            "Medical document analysis failed."
        );
      }

      return data;
    };

  // =========================================================
  // DOCUMENT RESPONSE
  // =========================================================

  const createDocumentResponse = (data) => {
    if (
      typeof data.final_summary ===
      "string"
    ) {
      return data.final_summary.trim();
    }

    if (
      data.language?.translated_text
    ) {
      return String(
        data.language.translated_text
      ).trim();
    }

    if (
      data.doctor_visit
        ?.doctor_visit_summary
    ) {
      return String(
        data.doctor_visit
          .doctor_visit_summary
      ).trim();
    }

    if (
      data.clinical_analysis?.summary
    ) {
      return String(
        data.clinical_analysis.summary
      ).trim();
    }

    return "The medical report was processed successfully. Please review the findings with a qualified healthcare professional.";
  };

  // =========================================================
  // ANALYZE UPLOADED FILE
  // =========================================================

  const analyzeUploadedFile = async (
    file
  ) => {
    setUploading(true);
    setLoading(true);

    setUploadStatus(
      `Preparing ${file.name}...`
    );

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content:
          `Uploaded medical report: ${file.name}`,
        isFile: true,
      },
    ]);

    updateWorkflow([
      {
        name: "Medical report uploaded",
        status: "completed",
      },
      {
        name: "Extracting report text",
        status: "running",
      },
      {
        name: "Medical analysis",
        status: "waiting",
      },
      {
        name: "Safety check",
        status: "waiting",
      },
    ]);

    try {
      // =====================================================
      // EXTRACT REPORT
      // =====================================================

      const documentText =
        await extractDocumentText(file);

      if (
        !documentText ||
        documentText.length < 10
      ) {
        throw new Error(
          "I could not read enough text from this report. Please upload a clearer report."
        );
      }

      console.log("EXTRACTED REPORT TEXT:", documentText);
  

      setUploadStatus(
        "Report extracted. Analyzing..."
      );

      updateWorkflow([
        {
          name: "Medical report uploaded",
          status: "completed",
        },
        {
          name: "Extracting report text",
          status: "completed",
        },
        {
          name: "Medical analysis",
          status: "running",
        },
        {
          name: "Safety check",
          status: "waiting",
        },
      ]);

      // =====================================================
      // ANALYZE REPORT
      // =====================================================

      const data =
        await analyzeDocumentWithBackend(
          documentText
        );

      console.log(
        "FULL ANALYZED REPORT:",
        data
      );

      // =====================================================
      // SAVE REPORT CONTEXT
      // =====================================================

      setReportContext({
        ...data,

        original_report_text:
          documentText,

        file_name:
          file.name,
      });

      console.log(
        "REPORT CONTEXT SAVED FOR MEDISAATHI:",
        {
          ...data,
          original_report_text:
            documentText,
          file_name:
            file.name,
        }
      );

      // =====================================================
      // CREATE DISPLAY RESPONSE
      // =====================================================

      const assistantResponse =
        createDocumentResponse(data);

      updateWorkflow([
        {
          name: "Medical report uploaded",
          status: "completed",
        },
        {
          name: "Extracting report text",
          status: "completed",
        },
        {
          name: "Medical analysis",
          status: "completed",
        },
        {
          name: "Safety check",
          status: "completed",
        },
      ]);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: assistantResponse,
        },
      ]);

      speakResponse(assistantResponse);

      setUploadStatus(
        "Report analyzed successfully. MediSaathi can now answer questions about this report."
      );
    } catch (error) {
      console.error(
        "Report analysis error:",
        error
      );

      const errorMessage =
        error?.message ||
        "I could not analyze the report.";

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: errorMessage,
        },
      ]);

      updateWorkflow([
        {
          name: "Medical report uploaded",
          status: "completed",
        },
        {
          name: "Report analysis",
          status: "failed",
        },
      ]);

      setUploadStatus(
        "Report analysis failed."
      );
    } finally {
      setUploading(false);
      setLoading(false);
    }
  };

  // =========================================================
  // NAVIGATION
  // =========================================================

  const navigate = (page) => {
    stopSpeaking();
    setActivePage(page);
  };

  // =========================================================
  // DASHBOARD
  // =========================================================

  const Dashboard = () => {
    return (
      <div className="page">

        {/* PAGE HEADER */}
        <div className="page-heading">
          <div>
            <p className="eyebrow">
              GOOD MORNING
            </p>

            <h1>
              Welcome back, Jahnavi
            </h1>

            <p className="page-subtitle">
              Manage your personal health information
              securely with CareVault.
            </p>
          </div>

          <button
            className="primary-button"
            onClick={openFilePicker}
          >
            + Upload Report
          </button>
        </div>

        {/* STATS */}
        <div className="stats-grid">

          <div className="stat-card">
            <div className="stat-icon blue">
              📄
            </div>

            <div>
              <span>My Reports</span>
              <strong>4</strong>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon green">
              💊
            </div>

            <div>
              <span>Medicines</span>
              <strong>2</strong>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon purple">
              📊
            </div>

            <div>
              <span>Health Trends</span>
              <strong>Active</strong>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon orange">
              🤖
            </div>

            <div>
              <span>AI Assistance</span>
              <strong>Active</strong>
            </div>
          </div>

        </div>

        {/* HEALTH & SAFETY */}
        <div className="section-heading">
          <div>
            <h2>
              Health & Safety
            </h2>

            <p>
              Quick access to important healthcare
              safety assistance.
            </p>
          </div>
        </div>

        {/* SAFETY CARDS */}
        <div className="dashboard-grid">

          <div className="safety-dashboard-card">

            <div className="safety-dashboard-icon">
              🛡️
            </div>

            <h3>
              Safety Check
            </h3>

            <p>
              Check health information for important
              safety considerations and know when
              professional help may be needed.
            </p>

            <button
              className="primary-button"
              onClick={() => {
                navigate("assistant");

                setTimeout(() => {
                  setMessage(
                    "Perform a safety check based on my health information."
                  );
                }, 100);
              }}
            >
              Run Safety Check
            </button>

          </div>

          <div className="dashboard-card safety-dashboard-info">

            <div className="card-header">
              <div>
                <h3>
                  Safety First
                </h3>

                <p>
                  Important healthcare guidance
                </p>
              </div>
            </div>

            <div className="safety-alert">
              🛡️ MediSaathi provides information and
              assistance only. It does not diagnose
              conditions, prescribe medicines, or replace
              professional medical care.
            </div>

          </div>

        </div>

        {/* RECENT REPORTS + MEDISAATHI */}
        <div className="dashboard-grid">

          {/* RECENT REPORTS */}
          <div className="dashboard-card">

            <div className="card-header">
              <div>
                <h3>
                  Recent Reports
                </h3>

                <p>
                  Your latest medical documents
                </p>
              </div>
            </div>

            <div className="report-list">

              <div className="report-row">

                <div className="report-icon">
                  🧪
                </div>

                <div className="report-info">
                  <strong>
                    Blood Test Report
                  </strong>

                  <span>
                    Uploaded 2 days ago
                  </span>
                </div>

                <span className="status-badge">
                  Analyzed
                </span>

              </div>

              <div className="report-row">

                <div className="report-icon">
                  🧪
                </div>

                <div className="report-info">
                  <strong>
                    Complete Blood Count
                  </strong>

                  <span>
                    Uploaded 1 week ago
                  </span>
                </div>

                <span className="status-badge">
                  Analyzed
                </span>

              </div>

              <div className="report-row">

                <div className="report-icon">
                  🩺
                </div>

                <div className="report-info">
                  <strong>
                    Health Checkup
                  </strong>

                  <span>
                    Uploaded 2 weeks ago
                  </span>
                </div>

                <span className="status-badge">
                  Analyzed
                </span>

              </div>

            </div>

          </div>

          {/* MEDISAATHI */}
          <div className="dashboard-card">

            <div className="card-header">

              <div>
                <h3>
                  MediSaathi AI
                </h3>

                <p>
                  Your healthcare assistant
                </p>
              </div>

              <div className="online-indicator">
                <span></span>
                Online
              </div>

            </div>

            <div className="ai-card-content">

              <div className="ai-large-icon">
                ✦
              </div>

              <p>
                Understand reports, medicines, health
                trends and prepare for doctor visits
                using natural language.
              </p>

              <button
                className="primary-button full"
                onClick={() =>
                  navigate("assistant")
                }
              >
                Open MediSaathi AI
              </button>

            </div>

          </div>

        </div>

      </div>
    );
  };

  // =========================================================
  // REPORTS
  // =========================================================

  const ReportsPage = () => (
    <div className="page">

      <div className="page-heading">

        <div>
          <p className="eyebrow">
            HEALTH RECORDS
          </p>

          <h1>
            Medical Reports
          </h1>

          <p className="page-subtitle">
            Keep your medical documents organized
            and use MediSaathi to understand them.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={openFilePicker}
        >
          + Upload Report
        </button>

      </div>

      <div className="dashboard-card">

        <div className="card-header">

          <div>
            <h3>
              Your Reports
            </h3>

            <p>
              4 medical documents in your
              CareVault
            </p>
          </div>

        </div>

        <div className="report-list full-list">

          {[
            [
              "Blood Test Report",
              "2 days ago",
              "🧪",
            ],
            [
              "Complete Blood Count",
              "1 week ago",
              "🩸",
            ],
            [
              "Health Checkup",
              "2 weeks ago",
              "🩺",
            ],
            [
              "Thyroid Profile",
              "1 month ago",
              "🔬",
            ],
          ].map((report) => (
            <div
              className="report-row"
              key={report[0]}
            >

              <div className="report-icon">
                {report[2]}
              </div>

              <div className="report-info">

                <strong>
                  {report[0]}
                </strong>

                <span>
                  Uploaded {report[1]}
                </span>

              </div>

              <span className="status-badge">
                Analyzed
              </span>

              <button className="small-button">
                View
              </button>

            </div>
          ))}

        </div>

      </div>

    </div>
  );

  // =========================================================
  // MEDICINES
  // =========================================================

  const MedicinesPage = () => (
    <div className="page">

      <div className="page-heading">

        <div>
          <p className="eyebrow">
            MEDICATIONS
          </p>

          <h1>
            Medicines
          </h1>

          <p className="page-subtitle">
            Keep track of medicines identified
            from your health information.
          </p>
        </div>

      </div>

      <div className="medicine-grid">

        <div className="medicine-card">

          <div className="medicine-icon">
            💊
          </div>

          <div>

            <h3>
              Medicine information
            </h3>

            <p>
              Ask MediSaathi about a medicine,
              its general purpose, or important
              safety information.
            </p>

          </div>

          <button
            className="outline-button"
            onClick={() => {
              setActivePage("assistant");

              setTimeout(() => {
                setMessage(
                  "Give me information about my medicines and important safety points."
                );
              }, 100);
            }}
          >
            Ask MediSaathi
          </button>

        </div>

        <div className="medicine-card">

          <div className="medicine-icon">
            📋
          </div>

          <div>

            <h3>
              Medication list
            </h3>

            <p>
              Medicines detected from your
              uploaded medical information will
              appear here.
            </p>

          </div>

          <span className="coming-badge">
            Connected to reports
          </span>

        </div>

      </div>

    </div>
  );

  // =========================================================
  // TRENDS
  // =========================================================

  const TrendsPage = () => (
    <div className="page">

      <div className="page-heading">

        <div>
          <p className="eyebrow">
            HEALTH MONITORING
          </p>

          <h1>
            Health Trends
          </h1>

          <p className="page-subtitle">
            Understand changes across your
            historical health measurements.
          </p>
        </div>

      </div>

      <div className="trend-grid">

        <div className="trend-card">

          <div className="trend-card-top">
            <span>
              Hemoglobin
            </span>

            <span className="trend-up">
              Trend
            </span>
          </div>

          <strong>
            10.8 g/dL
          </strong>

          <p>
            Historical measurements can be
            compared by MediSaathi.
          </p>

        </div>

        <div className="trend-card">

          <div className="trend-card-top">

            <span>
              Blood Pressure
            </span>

            <span className="trend-neutral">
              Tracking
            </span>

          </div>

          <strong>
            —
          </strong>

          <p>
            Upload reports containing
            measurements to build your trend
            history.
          </p>

        </div>

        <div className="trend-card">

          <div className="trend-card-top">

            <span>
              Health Records
            </span>

            <span className="trend-up">
              Active
            </span>

          </div>

          <strong>
            4
          </strong>

          <p>
            Reports available for analysis.
          </p>

        </div>

      </div>

      <div className="dashboard-card trend-empty">

        <div className="trend-empty-icon">
          📈
        </div>

        <h3>
          More trends will appear here
        </h3>

        <p>
          Upload additional medical reports
          containing historical measurements
          and MediSaathi can help compare the
          available information.
        </p>

        <button
          className="primary-button"
          onClick={openFilePicker}
        >
          Upload Report
        </button>

      </div>

    </div>
  );

  // =========================================================
  // SAFETY PAGE
  // =========================================================

  const SafetyPage = () => (
    <div className="page">

      <div className="page-heading">

        <div>

          <p className="eyebrow">
            HEALTH & SAFETY
          </p>

          <h1>
            Safety Check
          </h1>

          <p className="page-subtitle">
            Get important safety guidance based on
            the health information you provide.
          </p>

        </div>

      </div>

      <div className="dashboard-grid">

        <div className="safety-dashboard-card">

          <div className="safety-dashboard-icon">
            🛡️
          </div>

          <h3>
            Health Safety Check
          </h3>

          <p>
            MediSaathi can help identify important
            safety considerations from the health
            information you provide.
          </p>

          <button
            className="primary-button"
            onClick={() => {
              navigate("assistant");

              setTimeout(() => {
                sendMessage(
                  "Perform a safety check based on my health information."
                );
              }, 100);
            }}
          >
            Run Safety Check
          </button>

        </div>

        <div className="dashboard-card safety-dashboard-info">

          <div className="card-header">

            <div>

              <h3>
                Safety First
              </h3>

              <p>
                Important healthcare guidance
              </p>

            </div>

          </div>

          <div className="safety-alert">

            🛡️ MediSaathi provides information and
            assistance only. It does not diagnose
            conditions, prescribe medicines, or replace
            professional medical care.

          </div>

        </div>

      </div>

      <div className="dashboard-card">

        <div className="card-header">

          <div>

            <h3>
              When to Seek Professional Help
            </h3>

            <p>
              Safety information to keep in mind
            </p>

          </div>

        </div>

        <div className="safety-alert">

          If you have severe, sudden, or emergency
          symptoms, seek immediate help from a
          qualified healthcare professional or local
          emergency service.

        </div>

      </div>

    </div>
  );

  // =========================================================
  // MEDISAATHI
  // =========================================================

  const AssistantPage = () => (
    <div className="assistant-page">

      <div className="assistant-header">

        <div className="assistant-brand-icon">
          ✦
        </div>

        <div>

          <p className="eyebrow">
            CAREVAULT AI
          </p>

          <h1>
            MediSaathi AI
          </h1>

          <p>
            Your multilingual healthcare
            information assistant
          </p>

        </div>

        <div className="online-indicator">
          <span></span>
          Online
        </div>

      </div>

      <div className="assistant-layout">

        <div className="assistant-chat">

          {messages.length === 0 ? (

            <div className="assistant-welcome">

              <div className="assistant-welcome-icon">
                ✦
              </div>

              <h2>
                How can MediSaathi help?
              </h2>

              <p>
                Ask questions naturally or
                upload a medical report.
              </p>

              <div className="assistant-actions">

                {quickActions.map(
                  (action) => (
                    <button
                      key={action.title}
                      onClick={() =>
                        sendMessage(
                          action.message
                        )
                      }
                    >

                      <span>
                        {action.icon}
                      </span>

                      {action.title}

                    </button>
                  )
                )}

              </div>

            </div>

          ) : (

            <div className="assistant-messages">

              {messages.map(
                (item, index) => (

                  <div
                    key={index}
                    className={`assistant-message ${item.role}`}
                  >

                    <div className="message-avatar">
                      {item.role ===
                      "assistant"
                        ? "✦"
                        : "J"}
                    </div>

                    <div className="message-content">

                      <span className="message-name">

                        {item.role ===
                        "assistant"
                          ? "MediSaathi"
                          : "You"}

                      </span>

                      <p>
                        {item.content}
                      </p>

                      {item.role ===
                        "assistant" && (

                        <button
                          className="message-speak"
                          onClick={() =>
                            speakResponse(
                              item.content
                            )
                          }
                        >
                          🔊 Listen
                        </button>

                      )}

                    </div>

                  </div>

                )
              )}

              {loading && (

                <div className="assistant-message assistant">

                  <div className="message-avatar">
                    ✦
                  </div>

                  <div className="message-content">

                    <span className="message-name">
                      MediSaathi
                    </span>

                    <div className="typing">
                      <i></i>
                      <i></i>
                      <i></i>
                    </div>

                  </div>

                </div>

              )}

            </div>

          )}

          {workflow.length > 0 && (

            <div className="workflow">

              {workflow.map(
                (step, index) => (

                  <div
                    key={index}
                    className={
                      step.status
                    }
                  >

                    <span>

                      {step.status ===
                      "completed"
                        ? "✓"
                        : step.status ===
                          "failed"
                        ? "!"
                        : "•"}

                    </span>

                    {step.name}

                  </div>

                )
              )}

            </div>

          )}

          {(isSpeaking ||
            isListening) && (

            <div className="voice-status">

              {isSpeaking &&
                "🔊 MediSaathi is speaking..."}

              {isListening &&
                "🎙️ Listening..."}

            </div>

          )}

          <div className="assistant-input">

            <button
              className="input-icon"
              onClick={openFilePicker}
              disabled={
                loading || uploading
              }
              title="Upload medical report"
            >
              📎
            </button>

            <textarea
              value={message}
              onChange={(event) =>
                setMessage(
                  event.target.value
                )
              }
              onKeyDown={(event) => {

                if (
                  event.key === "Enter" &&
                  !event.shiftKey
                ) {

                  event.preventDefault();

                  sendMessage();

                }

              }}
              placeholder={`Ask MediSaathi in ${language}...`}
              disabled={
                loading || uploading
              }
            />

            <button
              className={`input-icon ${
                isListening
                  ? "listening"
                  : ""
              }`}
              onClick={startListening}
              disabled={
                loading || uploading
              }
            >
              🎙️
            </button>

            {isSpeaking && (

              <button
                className="input-icon stop"
                onClick={stopSpeaking}
              >
                ■
              </button>

            )}

            <button
              className="send-button"
              onClick={() =>
                sendMessage()
              }
              disabled={
                loading ||
                uploading ||
                !message.trim()
              }
            >
              ↑
            </button>

          </div>

          <p className="assistant-disclaimer">

            MediSaathi provides health
            information and assistance only.
            It does not diagnose conditions,
            prescribe medicines, or replace
            professional medical advice.

          </p>

        </div>

        <aside className="assistant-side">

          <div className="assistant-side-card">

            <h3>
              Language
            </h3>

            <select
              value={language}
              onChange={(event) => {
                stopSpeaking();

                setLanguage(
                  event.target.value
                );
              }}
            >

              {languages.map(
                (item) => (

                  <option
                    key={item}
                    value={item}
                  >
                    {item}
                  </option>

                )
              )}

            </select>

          </div>

          <div className="assistant-side-card">

            <h3>
              Upload a Report
            </h3>

            <p>
              Upload a PDF or image and
              MediSaathi will extract and
              analyze the available text.
            </p>

            <button
              className="primary-button full"
              onClick={openFilePicker}
              disabled={
                uploading || loading
              }
            >
              {uploading
                ? "Processing..."
                : "Upload Report"}
            </button>

            {uploadStatus && (

              <div className="side-upload-status">
                {uploadStatus}
              </div>

            )}

          </div>

          <div className="assistant-side-card safety-card">

            <div className="safety-icon">
              🛡️
            </div>

            <h3>
              Safety First
            </h3>

            <p>
              Health information is handled
              with safety and permission in
              mind.
            </p>

          </div>

        </aside>

      </div>

    </div>
  );

  // =========================================================
  // MAIN CONTENT
  // =========================================================

  const renderPage = () => {

    switch (activePage) {

      case "dashboard":
        return <Dashboard />;

      case "reports":
        return <ReportsPage />;

      case "medicines":
        return <MedicinesPage />;

      case "trends":
        return <TrendsPage />;

      case "safety":
        return <SafetyPage />;

      case "assistant":
        return <AssistantPage />;

      default:
        return <Dashboard />;

    }

  };

  // =========================================================
  // APP
  // =========================================================

  return (
    <div className="carevault-app">

      {/* Hidden file input */}

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg"
        onChange={handleFileSelected}
        className="hidden-file-input"
      />

      {/* =====================================================
          SIDEBAR
      ====================================================== */}

      <aside className="sidebar">

        <div className="brand">

          <div className="brand-logo">
            C
          </div>

          <div>

            <h2>
              CareVault
            </h2>

            <span>
              Personal Health Vault
            </span>

          </div>

        </div>

        <div className="nav-section">

          <p>
            MAIN
          </p>

          <button
            className={
              activePage === "dashboard"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() =>
              navigate("dashboard")
            }
          >
            <span>
              ⌂
            </span>

            Dashboard
          </button>

          <button
            className={
              activePage === "reports"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() =>
              navigate("reports")
            }
          >
            <span>
              ▣
            </span>

            Medical Reports
          </button>

          <button
            className={
              activePage === "medicines"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() =>
              navigate("medicines")
            }
          >
            <span>
              ✚
            </span>

            Medicines
          </button>

          <button
            className={
              activePage === "trends"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() =>
              navigate("trends")
            }
          >
            <span>
              ⌁
            </span>

            Health Trends
          </button>

          <button
            className={
              activePage === "safety"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() =>
              navigate("safety")
            }
          >
            <span>
              🛡️
            </span>

            Safety
          </button>

        </div>

        <div className="nav-section">

          <p>
            ASSISTANT
          </p>

          <button
            className={
              activePage === "assistant"
                ? "nav-item ai-nav active"
                : "nav-item ai-nav"
            }
            onClick={() =>
              navigate("assistant")
            }
          >

            <span>
              ✦
            </span>

            MediSaathi AI

            <i></i>

          </button>

        </div>

        <div className="sidebar-bottom">

          <div className="secure-box">

            <div>
              🔐
            </div>

            <div>

              <strong>
                Your data, your control
              </strong>

              <p>
                Your personal health information
                stays under your control.
              </p>

            </div>

          </div>

          <div className="user-profile">

            <div className="user-avatar">
              J
            </div>

            <div>

              <strong>
                Jahnavi
              </strong>

              <span>
                Personal account
              </span>

            </div>

            <button>
              ⋮
            </button>

          </div>

        </div>

      </aside>

      {/* =====================================================
          MAIN
      ====================================================== */}

      <main className="main-area">

        <header className="top-header">

          <div className="mobile-brand">
            CareVault
          </div>

          <div className="header-actions">

            <button
              className="header-icon"
              title="Notifications"
            >
              ♧
              <i></i>
            </button>

            <div className="header-user">

              <div className="user-avatar small">
                J
              </div>

              <div>

                <strong>
                  Jahnavi
                </strong>

                <span>
                  My Account
                </span>

              </div>

            </div>

          </div>

        </header>

        {renderPage()}

      </main>

    </div>
  );
}

export default App;