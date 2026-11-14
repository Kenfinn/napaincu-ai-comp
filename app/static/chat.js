/* Ask FEAF floating chat panel & multi-turn conversation script (C4).
   Vanilla JS, no frameworks, strict textContent rendering. */
(function () {
  "use strict";

  var KUNCI_SIMPAN = "feaf_chat";
  var KUNCI_BUKA = "feaf_chat_buka";
  var MAKS_PESAN = 12;

  function muatRiwayat() {
    try {
      var mentah = window.sessionStorage.getItem(KUNCI_SIMPAN);
      if (!mentah) return [];
      var daftar = JSON.parse(mentah);
      return Array.isArray(daftar) ? daftar.slice(-MAKS_PESAN) : [];
    } catch (_e) {
      return [];
    }
  }

  function simpanRiwayat(daftar) {
    try {
      var potong = (daftar || []).slice(-MAKS_PESAN);
      window.sessionStorage.setItem(KUNCI_SIMPAN, JSON.stringify(potong));
    } catch (_e) {
      /* ignore quota/storage errors */
    }
  }

  function formatTautanLabel(tplBuka, jalur) {
    if (!tplBuka) return jalur + " \u2192";
    return tplBuka.replace("{jalur}", jalur);
  }

  function buatElemenPesan(item, label) {
    var bungkus = document.createElement("div");
    var peran = item.peran === "user" ? "user" : "asisten";
    bungkus.className = "cp-pesan cp-pesan-" + peran;

    var teks = document.createElement("div");
    teks.className = "cp-pesan-teks";
    teks.textContent = item.teks || "";
    bungkus.appendChild(teks);

    if (peran === "asisten") {
      if (item.jalur === "template_setelah_tolak" && label.catatanTolak) {
        var cat = document.createElement("div");
        cat.className = "cp-catatan-tolak";
        cat.textContent = label.catatanTolak;
        bungkus.appendChild(cat);
      }

      if (Array.isArray(item.tautan) && item.tautan.length > 0) {
        var barisTautan = document.createElement("div");
        barisTautan.className = "cp-tautan-baris";
        for (var i = 0; i < item.tautan.length; i++) {
          var t = String(item.tautan[i] || "");
          if (t.charAt(0) !== "/") continue;
          var a = document.createElement("a");
          a.className = "cp-pil-tautan";
          a.href = t;
          a.textContent = formatTautanLabel(label.bukaHalaman, t);
          barisTautan.appendChild(a);
        }
        if (barisTautan.childNodes.length > 0) {
          bungkus.appendChild(barisTautan);
        }
      }

      if ((Array.isArray(item.sumber) && item.sumber.length > 0) || item.id) {
        var meta = document.createElement("div");
        meta.className = "cp-meta-baris";

        var blokSumber = document.createElement("span");
        if (Array.isArray(item.sumber) && item.sumber.length > 0) {
          blokSumber.textContent = (label.sumber || "Sources:") + " ";
          for (var j = 0; j < item.sumber.length; j++) {
            if (j > 0) {
              blokSumber.appendChild(document.createTextNode(" \u00b7 "));
            }
            var s = String(item.sumber[j] || "");
            var bag = s.split(" ")[0];
            if (bag.indexOf("http") === 0 || bag.charAt(0) === "/") {
              var tautS = document.createElement("a");
              tautS.href = bag;
              tautS.textContent = s;
              blokSumber.appendChild(tautS);
            } else {
              blokSumber.appendChild(document.createTextNode(s));
            }
          }
        }
        meta.appendChild(blokSumber);

        if (item.id) {
          var tautJejak = document.createElement("a");
          tautJejak.href = "/api/ask/traces/" + encodeURIComponent(item.id);
          tautJejak.target = "_blank";
          tautJejak.rel = "noopener";
          tautJejak.textContent = (label.jejak || "Trace") + " #" + String(item.id).slice(-6);
          meta.appendChild(tautJejak);
        }
        bungkus.appendChild(meta);
      }
    }
    return bungkus;
  }

  function pasangWadahChat(akar, modePanel) {
    if (!akar) return;
    var ds = akar.dataset;
    var konteks = {
      halaman: ds.halaman || "",
      kode: ds.kode || "",
      id: ds.id || ""
    };
    var bahasa = ds.bahasa || "en";
    var label = {
      kosong: ds.teksKosong || "",
      memuat: ds.teksMemuat || "...",
      galatJaringan: ds.teksGalatJaringan || "Network error.",
      galatAkses: ds.teksGalatAkses || "Access code required.",
      sumber: ds.teksSumber || "Sources:",
      bukaHalaman: ds.teksBukaHalaman || "Open {jalur} \u2192",
      jejak: ds.teksJejak || "Trace",
      catatanTolak: ds.teksCatatanTolak || ""
    };

    var elDisclaimer = akar.querySelector(".cp-disclaimer");
    if (elDisclaimer && ds.d1 !== undefined) {
      elDisclaimer.textContent = (ds.d1 || "") + (ds.d2 || "");
    }

    var elDaftar = akar.querySelector(".cp-daftar");
    var elForm = akar.querySelector(".cp-form");
    var elInput = akar.querySelector(".cp-input");
    var elKirim = akar.querySelector(".cp-kirim");
    var elRecap = akar.querySelector(".cp-aksi-recap");
    var elBaru = akar.querySelector(".cp-aksi-baru");
    var chips = akar.querySelectorAll(".cp-chip");

    function renderDaftar(animasiTerakhir) {
      if (!elDaftar) return;
      while (elDaftar.firstChild) {
        elDaftar.removeChild(elDaftar.firstChild);
      }
      var riwayat = muatRiwayat();
      if (riwayat.length === 0) {
        var kosong = document.createElement("div");
        kosong.className = "cp-kosong";
        kosong.textContent = label.kosong;
        elDaftar.appendChild(kosong);
        return;
      }
      for (var i = 0; i < riwayat.length; i++) {
        var elPesan = buatElemenPesan(riwayat[i], label);
        if (animasiTerakhir && i === riwayat.length - 1) {
          elPesan.classList.add("cp-pesan-masuk");
        }
        elDaftar.appendChild(elPesan);
      }
      elDaftar.scrollTop = elDaftar.scrollHeight;
    }

    function kirimPertanyaan(teksPertanyaan, jenisKhusus) {
      var q = String(teksPertanyaan || "").trim();
      if (!q && jenisKhusus !== "recap") return;
      var riwayatLama = muatRiwayat();
      var riwayatKirim = riwayatLama.map(function (it) {
        return {
          peran: it.peran,
          teks: it.teks,
          id: it.id || "",
          tanda: it.tanda || ""
        };
      });

      var teksTampil = jenisKhusus === "recap" && !q ? (elRecap ? elRecap.textContent : "Recap") : q;
      var daftarSekarang = riwayatLama.slice();
      if (jenisKhusus !== "recap") {
        daftarSekarang.push({ peran: "user", teks: teksTampil });
        simpanRiwayat(daftarSekarang);
      }
      renderDaftar(jenisKhusus !== "recap");

      var elMemuat = document.createElement("div");
      elMemuat.className = "cp-pesan cp-pesan-asisten cp-pesan-masuk";
      elMemuat.setAttribute("role", "status");
      elMemuat.setAttribute("aria-label", label.memuat);
      var titik = document.createElement("div");
      titik.className = "cp-mengetik";
      titik.setAttribute("aria-hidden", "true");
      for (var d = 0; d < 3; d++) {
        titik.appendChild(document.createElement("span"));
      }
      var teksSr = document.createElement("span");
      teksSr.className = "cp-sr-only";
      teksSr.textContent = "\u2026 " + label.memuat;
      elMemuat.appendChild(titik);
      elMemuat.appendChild(teksSr);
      if (elDaftar) {
        elDaftar.appendChild(elMemuat);
        elDaftar.scrollTop = elDaftar.scrollHeight;
      }

      if (elInput && jenisKhusus !== "recap") {
        elInput.value = "";
      }
      if (elKirim) elKirim.disabled = true;

      var payload = {
        pertanyaan: teksTampil,
        bahasa: bahasa,
        riwayat: riwayatKirim,
        konteks: konteks
      };
      if (jenisKhusus) {
        payload.jenis = jenisKhusus;
      }

      window.fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      })
        .then(function (resp) {
          if (resp.status === 401) {
            throw { kode: 401 };
          }
          if (!resp.ok) {
            throw { kode: resp.status };
          }
          return resp.json();
        })
        .then(function (data) {
          if (elKirim) elKirim.disabled = false;
          var itemAsisten = {
            peran: "asisten",
            teks: data.jawaban || "",
            id: data.id || "",
            tanda: data.tanda || "",
            sumber: data.sumber || [],
            tautan: data.tautan || [],
            jalur: data.jalur || ""
          };
          if (jenisKhusus === "recap") {
            if (elMemuat.parentNode) {
              elMemuat.parentNode.removeChild(elMemuat);
            }
            if (elDaftar) {
              var elU = buatElemenPesan({ peran: "user", teks: teksTampil }, label);
              var elA = buatElemenPesan(itemAsisten, label);
              elU.classList.add("cp-pesan-masuk");
              elA.classList.add("cp-pesan-masuk");
              elDaftar.appendChild(elU);
              elDaftar.appendChild(elA);
              elDaftar.scrollTop = elDaftar.scrollHeight;
            }
          } else {
            daftarSekarang.push(itemAsisten);
            simpanRiwayat(daftarSekarang);
            renderDaftar(true);
          }
        })
        .catch(function (err) {
          if (elKirim) elKirim.disabled = false;
          if (elMemuat.parentNode) {
            elMemuat.parentNode.removeChild(elMemuat);
          }
          var pesanGalat = err && err.kode === 401 ? label.galatAkses : label.galatJaringan;
          if (elDaftar) {
            var elG = buatElemenPesan({ peran: "asisten", teks: pesanGalat }, label);
            elG.classList.add("cp-pesan-masuk");
            elDaftar.appendChild(elG);
            elDaftar.scrollTop = elDaftar.scrollHeight;
          }
        });
    }

    if (elForm) {
      elForm.addEventListener("submit", function (ev) {
        ev.preventDefault();
        if (elInput) {
          kirimPertanyaan(elInput.value, null);
        }
      });
    }

    if (elInput) {
      elInput.addEventListener("keydown", function (ev) {
        if (ev.key === "Enter" && !ev.shiftKey) {
          ev.preventDefault();
          kirimPertanyaan(elInput.value, null);
        }
      });
    }

    if (elRecap) {
      elRecap.addEventListener("click", function (ev) {
        ev.preventDefault();
        kirimPertanyaan(elRecap.getAttribute("data-q") || "Recap", "recap");
      });
    }

    if (elBaru) {
      elBaru.addEventListener("click", function (ev) {
        ev.preventDefault();
        simpanRiwayat([]);
        renderDaftar();
        if (elInput) elInput.focus();
      });
    }

    for (var c = 0; c < chips.length; c++) {
      chips[c].addEventListener("click", function (ev) {
        ev.preventDefault();
        var q = this.getAttribute("data-q") || this.textContent;
        kirimPertanyaan(q, null);
      });
    }

    renderDaftar();

    if (modePanel) {
      var fab = document.getElementById("cp-fab");
      var panel = document.getElementById("cp-panel");
      var latar = document.getElementById("cp-latar");
      var tutup = document.getElementById("cp-tutup");
      var tutupTimer = null;
      var tutupHandler = null;
      var bukaFrame = null;

      function kurangiGerak() {
        return !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
      }

      function batalkanBuka() {
        if (bukaFrame !== null) {
          if (window.cancelAnimationFrame) {
            window.cancelAnimationFrame(bukaFrame);
          } else {
            window.clearTimeout(bukaFrame);
          }
          bukaFrame = null;
        }
      }

      function batalkanTutup() {
        if (tutupTimer !== null) {
          window.clearTimeout(tutupTimer);
          tutupTimer = null;
        }
        if (panel && tutupHandler) {
          panel.removeEventListener("transitionend", tutupHandler);
          tutupHandler = null;
        }
      }

      function bukaPanel(fokusInput, langsung) {
        if (!panel) return;
        batalkanBuka();
        batalkanTutup();
        var tanpaAnimasi = Boolean(langsung) || kurangiGerak();
        if (tanpaAnimasi) {
          panel.classList.add("cp-tanpa-animasi", "cp-buka");
          if (latar) latar.classList.add("cp-tanpa-animasi", "cp-buka");
          panel.hidden = false;
          if (latar) latar.hidden = false;
          void panel.offsetWidth;
          panel.classList.remove("cp-tanpa-animasi");
          if (latar) latar.classList.remove("cp-tanpa-animasi");
        } else {
          panel.classList.remove("cp-buka");
          if (latar) latar.classList.remove("cp-buka");
          panel.hidden = false;
          if (latar) latar.hidden = false;
          void panel.offsetWidth;
          var jadwalkan = window.requestAnimationFrame || function (fn) { return window.setTimeout(fn, 16); };
          bukaFrame = jadwalkan(function () {
            bukaFrame = null;
            panel.classList.add("cp-buka");
            if (latar) latar.classList.add("cp-buka");
          });
        }
        if (fab) fab.setAttribute("aria-expanded", "true");
        try {
          window.sessionStorage.setItem(KUNCI_BUKA, "1");
        } catch (_e) {}
        renderDaftar();
        if (fokusInput && elInput) {
          elInput.focus();
        }
      }

      function tutupPanel(fokusFab) {
        if (!panel) return;
        batalkanBuka();
        batalkanTutup();
        if (fab) fab.setAttribute("aria-expanded", "false");
        try {
          window.sessionStorage.removeItem(KUNCI_BUKA);
        } catch (_e) {}

        function selesaiTutup() {
          batalkanTutup();
          panel.hidden = true;
          if (latar) latar.hidden = true;
          if (fokusFab && fab) {
            fab.focus();
          }
        }

        if (panel.hidden || kurangiGerak()) {
          panel.classList.remove("cp-buka");
          if (latar) latar.classList.remove("cp-buka");
          selesaiTutup();
          return;
        }

        panel.classList.remove("cp-buka");
        if (latar) latar.classList.remove("cp-buka");
        tutupHandler = function (ev) {
          if (ev.target !== panel) return;
          selesaiTutup();
        };
        panel.addEventListener("transitionend", tutupHandler);
        tutupTimer = window.setTimeout(selesaiTutup, 300);
      }

      if (fab) {
        fab.addEventListener("click", function (ev) {
          ev.preventDefault();
          if (panel && !panel.hidden && panel.classList.contains("cp-buka")) {
            tutupPanel(true);
          } else {
            bukaPanel(true, false);
          }
        });
      }
      if (tutup) {
        tutup.addEventListener("click", function (ev) {
          ev.preventDefault();
          tutupPanel(true);
        });
      }
      if (latar) {
        latar.addEventListener("click", function () {
          tutupPanel(true);
        });
      }
      document.addEventListener("keydown", function (ev) {
        if (ev.key === "Escape" && panel && !panel.hidden) {
          ev.preventDefault();
          tutupPanel(true);
        }
      });

      try {
        if (window.sessionStorage.getItem(KUNCI_BUKA) === "1") {
          bukaPanel(false, true);
        }
      } catch (_e) {}
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    pasangWadahChat(document.getElementById("cp-akar"), true);
    pasangWadahChat(document.getElementById("cp-halaman-akar"), false);
  });
})();
