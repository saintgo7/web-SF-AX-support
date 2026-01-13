import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

export interface PDFOptions {
  filename?: string;
  format?: 'a4' | 'letter';
  orientation?: 'portrait' | 'landscape';
  margin?: number;
  scale?: number;
}

const defaultOptions: Required<PDFOptions> = {
  filename: 'document.pdf',
  format: 'a4',
  orientation: 'portrait',
  margin: 10,
  scale: 2,
};

/**
 * HTML 요소를 PDF로 변환하여 다운로드
 */
export async function generatePDF(
  element: HTMLElement,
  options?: PDFOptions
): Promise<void> {
  const opts = { ...defaultOptions, ...options };

  // A4 크기 (mm)
  const pageWidth = opts.orientation === 'portrait' ? 210 : 297;
  const pageHeight = opts.orientation === 'portrait' ? 297 : 210;

  // 캔버스로 캡처 (scale은 html2canvas에서 지원하지만 타입에 누락됨)
  const canvas = await html2canvas(element, {
    scale: opts.scale,
    useCORS: true,
    allowTaint: true,
    backgroundColor: '#ffffff',
    logging: false,
  } as Parameters<typeof html2canvas>[1]);

  const imgData = canvas.toDataURL('image/png');
  const imgWidth = pageWidth - opts.margin * 2;
  const imgHeight = (canvas.height * imgWidth) / canvas.width;

  // PDF 생성
  const pdf = new jsPDF({
    orientation: opts.orientation,
    unit: 'mm',
    format: opts.format,
  });

  // 여러 페이지 처리
  let heightLeft = imgHeight;
  let position = opts.margin;
  const pageContentHeight = pageHeight - opts.margin * 2;

  // 첫 페이지
  pdf.addImage(imgData, 'PNG', opts.margin, position, imgWidth, imgHeight);
  heightLeft -= pageContentHeight;

  // 추가 페이지
  while (heightLeft > 0) {
    position = heightLeft - imgHeight + opts.margin;
    pdf.addPage();
    pdf.addImage(imgData, 'PNG', opts.margin, position, imgWidth, imgHeight);
    heightLeft -= pageContentHeight;
  }

  // 다운로드
  pdf.save(opts.filename);
}

/**
 * 파일명 생성 (특수문자 제거)
 */
export function sanitizeFilename(title: string): string {
  return title
    .replace(/[<>:"/\\|?*]/g, '')
    .replace(/\s+/g, '_')
    .substring(0, 100);
}

/**
 * 보고서용 파일명 생성
 */
export function generateReportFilename(title: string, date?: string): string {
  const sanitized = sanitizeFilename(title);
  const dateStr = date || new Date().toISOString().split('T')[0];
  return `${sanitized}_${dateStr}.pdf`;
}
