import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { format } from "date-fns";
import { CalendarIcon, Save, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { apiClient } from "@/lib/api";
import { toast } from "sonner";

export const ExamWeekSettings = () => {
  const [startDate, setStartDate] = useState<Date>();
  const [endDate, setEndDate] = useState<Date>();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  // Load current exam week settings
  useEffect(() => {
    const loadSettings = async () => {
      try {
        setLoading(true);
        const response = await apiClient.getExamWeekSettings();
        if (response.success && response.data) {
          if (response.data.start_date) {
            setStartDate(new Date(response.data.start_date));
          }
          if (response.data.end_date) {
            setEndDate(new Date(response.data.end_date));
          }
        }
      } catch (error) {
        console.error('Error loading exam week settings:', error);
        toast.error('Sınav haftası ayarları yüklenirken hata oluştu');
      } finally {
        setLoading(false);
      }
    };

    loadSettings();
  }, []);

  const handleSave = async () => {
    if (!startDate || !endDate) {
      toast.error("Lütfen başlangıç ve bitiş tarihlerini seçin!");
      return;
    }

    if (startDate >= endDate) {
      toast.error("Başlangıç tarihi bitiş tarihinden önce olmalıdır!");
      return;
    }

    setSaving(true);
    try {
      const settings = {
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0]
      };

      const response = await apiClient.saveExamWeekSettings(settings);
      if (response.success) {
        toast.success("Sınav haftası aralığı başarıyla kaydedildi!");
      } else {
        toast.error(response.message || "Kaydetme sırasında hata oluştu");
      }
    } catch (error) {
      console.error('Error saving exam week settings:', error);
      toast.error('Kaydetme sırasında hata oluştu');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin" />
        <span className="ml-2">Ayarlar yükleniyor...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-2">Sınav Haftası Aralığı</h3>
        <p className="text-gray-600">
          Sınavların yapılabileceği tarih aralığını belirleyin. 
          Hocalar sadece bu tarihler arasından tercih yapabilecekler.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label>Başlangıç Tarihi</Label>
          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                className={cn(
                  "w-full justify-start text-left font-normal",
                  !startDate && "text-muted-foreground"
                )}
                disabled={saving}
              >
                <CalendarIcon className="mr-2 h-4 w-4" />
                {startDate ? format(startDate, "dd/MM/yyyy") : "Başlangıç tarihi seçin"}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <Calendar
                mode="single"
                selected={startDate}
                onSelect={setStartDate}
                disabled={(date) => date < new Date()}
                initialFocus
                className="pointer-events-auto"
              />
            </PopoverContent>
          </Popover>
        </div>

        <div className="space-y-2">
          <Label>Bitiş Tarihi</Label>
          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                className={cn(
                  "w-full justify-start text-left font-normal",
                  !endDate && "text-muted-foreground"
                )}
                disabled={saving}
              >
                <CalendarIcon className="mr-2 h-4 w-4" />
                {endDate ? format(endDate, "dd/MM/yyyy") : "Bitiş tarihi seçin"}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <Calendar
                mode="single"
                selected={endDate}
                onSelect={setEndDate}
                disabled={(date) => date < new Date() || (startDate && date <= startDate)}
                initialFocus
                className="pointer-events-auto"
              />
            </PopoverContent>
          </Popover>
        </div>
      </div>

      {startDate && endDate && (
        <div className="p-4 bg-blue-50 rounded-lg">
          <p className="text-sm text-blue-800">
            <strong>Seçilen Aralık:</strong> {format(startDate, "dd/MM/yyyy")} - {format(endDate, "dd/MM/yyyy")}
          </p>
          <p className="text-sm text-blue-600 mt-1">
            Bu tarihler arasında hocalar sınav tarihi tercihlerini yapabilecekler.
          </p>
          <p className="text-sm text-blue-600 mt-1">
            Hocalar en az 3 tarih seçmek zorundadır ve başka tarih giremezler.
          </p>
        </div>
      )}

      <Button 
        onClick={handleSave} 
        className="w-full" 
        disabled={!startDate || !endDate || saving}
      >
        {saving ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Kaydediliyor...
          </>
        ) : (
          <>
            <Save className="mr-2 h-4 w-4" />
            Aralığı Kaydet
          </>
        )}
      </Button>
    </div>
  );
};
