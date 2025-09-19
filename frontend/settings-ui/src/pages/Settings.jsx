// src/pages/Settings.jsx
import React, { useState, useEffect } from "react";
import {
  TextField,
  Checkbox,
  FormControlLabel,
  FormGroup,
  Typography,
  Box,
  Select,
  MenuItem,
  FormControl,
  Chip,
  Stepper,
  Step,
  StepLabel,
  Paper,
  IconButton,
  Button,
  Tooltip,
  Alert,
  AlertTitle,
  Collapse,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import LogoutIcon from "@mui/icons-material/Logout";
import SaveAltIcon from "@mui/icons-material/SaveAlt";
import ArrowBackIosNewIcon from "@mui/icons-material/ArrowBackIosNew";
import ArrowForwardIosIcon from "@mui/icons-material/ArrowForwardIos";
import SendIcon from "@mui/icons-material/Send";
import ScheduleIcon from "@mui/icons-material/Schedule";
import AddIcon from '@mui/icons-material/Add';
export default function Settings() {
  const steps = ["Days Back", "Time", "Frequency", "Mailing List", "Line Chart", "Bar Chart"];
  const [completed, setCompleted] = useState([false, false, false, false, false, false]);
  const [activeStep, setActiveStep] = useState(0);
  const [alertOpen, setAlertOpen] = useState(false);
  const [alertType, setAlertType] = useState("success");
  const [alertMsg, setAlertMsg] = useState("");

  const [daysBack, setDaysBack] = useState("");
  const [frequency, setFrequency] = useState("");
  const [day, setDay] = useState("");
  const [time, setTime] = useState("");
  const [emails, setEmails] = useState([]);
  const [emailInput, setEmailInput] = useState("");
  const [domain, setDomain] = useState("@nokia.com");
  const [lineType, setLineType] = useState("");
  const [barType, setBarType] = useState("");

  const [daysBackError, setDaysBackError] = useState("");
  const [timeError, setTimeError] = useState("");
  const [emailError, setEmailError] = useState("");

  const [lineEquation, setLineEquation] = useState("");
  const [barEquation, setBarEquation] = useState("");
  const [lineEqError, setLineEqError] = useState("");
  const [barEqError, setBarEqError] = useState("");
  const [lineSelectedKpis, setLineSelectedKpis] = useState([]);
  const [barSelectedKpis, setBarSelectedKpis] = useState([]);
  const [activeBtn, setActiveBtn] = useState(null);

  const nav = useNavigate();

  const kpiOptions = ["kpi001", "kpi002", "kpi003", "kpi004", "kpi005", "kpi006", "kpi007", "kpi008", "kpi009"];

  async function handleLogout() {
    try {
      await api.logout();
    } finally {
      localStorage.removeItem("token");
      nav("/login", { replace: true });
    }
  }

  function showAlert(type, msg) {
    setAlertType(type);
    setAlertMsg(msg);
    setAlertOpen(true);
    setTimeout(() => setAlertOpen(false), 4000);
  }

  // New reusable function
const addEmail = () => {
  if (emailInput.trim() !== "") {
    const regex = /^[a-zA-Z0-9._%+-]+$/;
    if (!regex.test(emailInput)) {
      setEmailError("Invalid email username");
      return;
    }
    const newEmail = emailInput + domain;
    setEmails((prev) => [...prev, newEmail]);
    setEmailInput("");
    setEmailError("");
  }
};

const handleEmailAdd = (e) => {
  if (e.key === "Enter") {
    addEmail();
  }
};


  const handleEmailDelete = (emailToDelete) => {
    setEmails((prev) => prev.filter((email) => email !== emailToDelete));
  };

  useEffect(() => {
    if (daysBack && (isNaN(Number(daysBack)) || parseInt(daysBack) <= 0)) {
      setDaysBackError("Must be a positive number greater than zero");
    } else setDaysBackError("");

    const timeRegex = /^([01]\d|2[0-3]):([0-5]\d)$/;
    if (time && !timeRegex.test(time)) {
      setTimeError("Enter a valid time (HH:MM, 24h)");
    } else setTimeError("");
  }, [daysBack, time]);

  useEffect(() => {
const eqRegex = /^(\s*(\(*\s*(kpi00[1-9]|\d+)\s*\)*)(\s*[-+*/]\s*(\(*\s*(kpi00[1-9]|\d+)\s*\)*))*)$/;
    if (lineType === "equation" && lineEquation && !eqRegex.test(lineEquation)) {
      setLineEqError("Invalid equation.");
    } else setLineEqError("");
    if (barType === "equation" && barEquation && !eqRegex.test(barEquation)) {
      setBarEqError("Invalid equation.");
    } else setBarEqError("");
  }, [lineEquation, barEquation, lineType, barType]);

  useEffect(() => {
    const updated = [...completed];
    updated[0] = daysBack !== "" && !daysBackError;
    updated[1] = time !== "" && !timeError;
    updated[2] =  frequency !== "";
    updated[3] = emails.length > 0;
    updated[4] = lineType !== "";
    updated[5] = barType !== "";
    setCompleted(updated);
  }, [daysBack, frequency, time, emails, lineType, barType, daysBackError, timeError]);

  const settings = {
    days_back: daysBack ? Number(daysBack) : undefined,
    frequency,
    days: day ? [day] : [],
    time,
    mailing_list: emails.join(";"),
    line_chart: lineType === "list" ? { type: "list", value: lineSelectedKpis } : { type: "equation", value: lineEquation },
    bar_chart: barType === "list" ? { type: "list", value: barSelectedKpis } : { type: "equation", value: barEquation },
  };

  useEffect(() => {
    async function fetchSettings() {
      try {
        const data = await api.getSettings();
        setDaysBack(data.days_back != null ? String(data.days_back) : "");
        setFrequency(data.frequency ?? "");
        setDay(data.days?.[0] || "");
        setTime(data.time ?? "");
        setEmails(data.mailing_list ? data.mailing_list.split(";") : []);
        if (data.line_chart?.type === "list") {
          setLineType("list");
          setLineSelectedKpis(data.line_chart.value || []);
        } else if (data.line_chart?.type === "equation") {
          setLineType("equation");
          setLineEquation(data.line_chart.value || "");
        }
        if (data.bar_chart?.type === "list") {
          setBarType("list");
          setBarSelectedKpis(data.bar_chart.value || []);
        } else if (data.bar_chart?.type === "equation") {
          setBarType("equation");
          setBarEquation(data.bar_chart.value || "");
        }
      } catch (e) {
        console.error("Failed to load settings", e);
      }
    }
    fetchSettings();
  }, []);


//key 
  useEffect(() => {
    async function saveSettings() {
      try {
        await api.saveSettings(settings);
      } catch (e) {
        console.error("Failed to save settings", e);
      }
    }
    saveSettings();
  }, [daysBack, frequency, day, time, emails, lineType, barType, lineSelectedKpis, barSelectedKpis, lineEquation, barEquation]);

  const images = ["/n1.jpg", "/n5.jpg", "/n2.jpg", "/n4.jpg", "/n14.jpg", "/n15.jpg", "/n60.jpg"];
  const [currentImage, setCurrentImage] = useState(0);
  useEffect(() => {
    const id = setInterval(() => {
      setCurrentImage((prev) => (prev + 1) % images.length);
    }, 4000);
    return () => clearInterval(id);
  }, [images.length]);

  return (
    <Box sx={{ height: "95vh", display: "flex", flexDirection: "column", justifyContent: "space-between", alignItems: "center", backgroundSize: "cover", position: "relative", backgroundPosition: "center", overflow: "hidden", p: 1 }}>
      {images.map((img, index) => (
        <Box key={index} sx={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", backgroundImage: `url(${img})`, backgroundSize: "cover", backgroundPosition: "center", transition: "opacity 1s ease-in-out", opacity: currentImage === index ? 1 : 0, zIndex: -1 }} />
      ))}

      <Paper elevation={9} sx={{ m: 1, p: 3, borderRadius: 3, maxWidth: 700, width: "100%", bgcolor: "rgba(255,255,255,0.95)", display: "flex", flexDirection: "column", gap: 2 }}>
        <Stepper alternativeLabel activeStep={activeStep} sx={{ "& .MuiStepLabel-root .Mui-completed": { color: "#56995B" }, "& .MuiStepLabel-root .Mui-active": { color: "#569099" }, "& .MuiStepLabel-label": { color: "#050833" } }}>
          {steps.map((label, index) => (
            <Step key={index} completed={completed[index]}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      <Paper elevation={6} sx={{ m: 1, p: 2, borderRadius: 3, maxWidth: 700, width: "100%", minHeight: 230, maxHeight: 230, display: "flex", flexDirection: "column", justifyContent: "space-between", bgcolor: "rgba(255,255,255,0.95)" }}>
        <Box sx={{ flexGrow: 1, overflowY: "auto", pr: 1, paddingTop: 2 }}>
          {activeStep === 0 && (
            <>
              <TextField fullWidth type="number" margin="normal" label="Days Back" value={daysBack} onChange={(e) => setDaysBack(e.target.value)} error={!!daysBackError} helperText={daysBackError} />
              <Typography variant="body2" color="text.secondary">Number of days back from present time to plot on the chart.</Typography>
            </>
          )}

          {activeStep === 1 && (
            <Box sx={{ pt: 1 }}>
              <TextField fullWidth label="Time (HH:MM)" placeholder="14:00" margin="normal" value={time} onChange={(e) => setTime(e.target.value)} error={!!timeError} helperText={timeError} />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1, textAlign: "center" }}>
                Time set at {time || "the set time"}
              </Typography>
            </Box>
          )}

          {activeStep === 2 && (
            <>
              <FormGroup row sx={{ justifyContent: "center", alignItems: "center", gap: 3 }}>
                {["daily", "weekly", "monthly"].map((f) => (
                  <FormControlLabel key={f} control={<Checkbox checked={frequency === f} onChange={() => setFrequency(f.toLowerCase())} />} label={f.charAt(0).toUpperCase() + f.slice(1)} />
                ))}
              </FormGroup>

              {frequency === "daily" && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1, textAlign: "center" }}>
                  The report will be sent daily at {time || "the set time"}
                </Typography>
              )}

              {(frequency === "weekly" || frequency === "monthly") && (
                <>
{frequency === "monthly" && (
  <TextField
    fullWidth
    label="Day"
    placeholder="Enter the date (e.g. 15)"
    value={day}
    onChange={(e) => setDay(e.target.value)}
    margin="normal"
  />
)}                  {frequency === "weekly" && (
  <>
    <TextField
      fullWidth
      label="Day"
      placeholder="Mon, Tue, Wed..."
      value={day}
      onChange={(e) => setDay(e.target.value)}
      margin="normal"
      error={day && !["Mon","Tue","Wed","Thu","Fri","Sat","Sun"].includes(day)}
      helperText={
        day && !["Mon","Tue","Wed","Thu","Fri","Sat","Sun"].includes(day)
          ? "Use 3-letter abbreviations (Mon, Tue, Wed, Thu, Fri, Sat, Sun)"
          : "Enter the day as 3-letter abbreviation (e.g., Mon, Tue, Wed)"
      }
    />
  </>
)}
                </>
              )}
            </>
          )}

          {activeStep === 3 && (
            <>
              <Box sx={{ display: "flex", gap: 3, justifyContent: "center", alignItems: "center", paddingTop: 2 }}>
                <TextField label="Enter email username" value={emailInput} onChange={(e) => setEmailInput(e.target.value)} onKeyDown={handleEmailAdd} error={!!emailError} helperText={emailError} />
                <FormControl>
                  <Select value={domain} onChange={(e) => setDomain(e.target.value)}>
                    <MenuItem value="@nokia.com">@nokia.com</MenuItem>
                    <MenuItem value="@gmail.com">@gmail.com</MenuItem>
                    <MenuItem value="@hotmail.com">@hotmail.com</MenuItem>
                  </Select>
                </FormControl>
                <IconButton onClick={addEmail} color="primary">
    <AddIcon />
  </IconButton>
              </Box>

              <Box sx={{ mt: 2, display: "flex", gap: 1, flexWrap: "wrap" }}>
                {emails.map((email, idx) => (
                  <Chip key={idx} label={email} onDelete={() => handleEmailDelete(email)} sx={{ bgcolor: "#C1C7C9", color: "#000" }} />
                ))}
              </Box>
            </>
          )}

          {activeStep === 4 && (
            <>
              <Typography variant="body1" color="text.secondary" sx={{ textAlign: "center", mb: 1, mt: -2 }}>
                Line Chart
              </Typography>
              <FormGroup row sx={{ justifyContent: "center", gap: 2 }}>
                <FormControlLabel control={<Checkbox checked={lineType === "list"} onChange={() => setLineType("list")} />} label="List" />
                <FormControlLabel control={<Checkbox checked={lineType === "equation"} onChange={() => setLineType("equation")} />} label="Equation" />
              </FormGroup>

              {lineType === "list" ? (
                <Box sx={{ display: "grid", gridTemplateColumns: "repeat(3, auto)", gap: "0.5rem 0rem", mt: 2, justifyItems: "center" }}>
                  {kpiOptions.map((kpi) => (
                    <Chip key={kpi} label={kpi} clickable onClick={() => setLineSelectedKpis((prev) => prev.includes(kpi) ? prev.filter((item) => item !== kpi) : [...prev, kpi])} sx={{ bgcolor: lineSelectedKpis.includes(kpi) ? "#154361" : "#E0E0E0", color: lineSelectedKpis.includes(kpi) ? "#fff" : "#000", fontWeight: lineSelectedKpis.includes(kpi) ? 600 : 400, width: "60%" }} />
                  ))}
                </Box>
              ) : (
                <TextField fullWidth label="Equation" margin="normal" value={lineEquation} onChange={(e) => setLineEquation(e.target.value)} error={!!lineEqError} helperText={lineEqError} />
              )}
            </>
          )}

          {activeStep === 5 && (
            <>
              <Typography variant="body1" color="text.secondary" sx={{ textAlign: "center", mb: 1, mt: -2 }}>
                Bar Chart
              </Typography>
              <FormGroup row sx={{ justifyContent: "center", gap: 2 }}>
                <FormControlLabel control={<Checkbox checked={barType === "list"} onChange={() => setBarType("list")} />} label="List" />
                <FormControlLabel control={<Checkbox checked={barType === "equation"} onChange={() => setBarType("equation")} />} label="Equation" />
              </FormGroup>

              {barType === "list" ? (
                <Box sx={{ display: "grid", gridTemplateColumns: "repeat(3, auto)", gap: "0.5rem 0rem", mt: 2, justifyItems: "center" }}>
                  {kpiOptions.map((kpi) => (
                    <Chip key={kpi} label={kpi} clickable onClick={() => setBarSelectedKpis((prev) => prev.includes(kpi) ? prev.filter((item) => item !== kpi) : [...prev, kpi])} sx={{ bgcolor: barSelectedKpis.includes(kpi) ? "#154361" : "#E0E0E0", color: barSelectedKpis.includes(kpi) ? "#fff" : "#000", fontWeight: barSelectedKpis.includes(kpi) ? 600 : 400, width: "60%" }} />
                  ))}
                </Box>
              ) : (
                <TextField fullWidth label="Equation" margin="normal" value={barEquation} onChange={(e) => setBarEquation(e.target.value)} error={!!barEqError} helperText={barEqError} />
              )}
            </>
          )}

          {activeStep === 6 && (
            <Box sx={{ textAlign: "center", mt: 0 }}>
              
    <Typography variant="body1" color="text.secondary" sx={{ mb: 1 }}>
      - If you need the email sent right away, press this button. This will not affect the scheduled send.
    </Typography>

              <Box sx={{ display: "flex", justifyContent: "center", gap: 3 }}>
                <Button
                  variant="contained"
                  startIcon={<SendIcon />}
                  sx={{ bgcolor: activeBtn === "send" ? "#56995B" : "#C4C8CC", color: "#fff", fontWeight: 600, borderRadius: 2, "&:hover": { bgcolor: activeBtn === "send" ? "#56995B" : "#777" } }}
                  onClick={async () => {
                    setActiveBtn("send");
                    try {
                      const me = await api.me();
                      const res = await api.sendEmail(me.email);
                      showAlert("success", res.message);
                    } catch (e) {
                      showAlert("error", e.message);
                    }
                  }}
                >
                  Send Email Now
                </Button>

                
              </Box>
            </Box>
          )}
        </Box>

        <Box sx={{ display: "flex", justifyContent: "space-between", mt: 2, pt: 2, borderTop: "1px solid #ddd" }}>
          <IconButton onClick={() => setActiveStep((prev) => Math.max(prev - 1, 0))} disabled={activeStep === 0}>
            <ArrowBackIosNewIcon />
          </IconButton>

         

          <IconButton onClick={() => setActiveStep((prev) => Math.min(prev + 1, 6))} disabled={activeStep === 6}>
            <ArrowForwardIosIcon />
          </IconButton>
        </Box>
      </Paper>

      <Box sx={{ position: "fixed", bottom: 27, right: 30, zIndex: 1000 }}>
        <Tooltip title="LogOut">
          <IconButton onClick={handleLogout} sx={{ bgcolor: "rgba(255,255,255,0.7)", color: "#000", fontWeight: 600, borderRadius: 2, "&:hover": { bgcolor: "rgba(255,255,255,0.9)" } }}>
            <LogoutIcon />
          </IconButton>
        </Tooltip>
        <Collapse in={alertOpen} sx={{ position: "fixed", top: 20, left: "50%", transform: "translateX(-50%)", zIndex: 2000, width: 400 }}>
          <Alert severity={alertType} onClose={() => setAlertOpen(false)} sx={{ borderRadius: 2, boxShadow: 3 }}>
            <AlertTitle>{alertType.charAt(0).toUpperCase() + alertType.slice(1)}</AlertTitle>
            {alertMsg}
          </Alert>
        </Collapse>
      </Box>
    </Box>
  );
}
