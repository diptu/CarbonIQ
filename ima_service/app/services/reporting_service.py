# # app/services/reporting_service.py
# from app.services.base_service import BaseService, log_method_call, log_action
# from app.models.reporting import Report


# class ReportingService(BaseService[Report]):
#     @log_method_call
#     def generate_report(self, report: Report) -> Report:
#         self.db.add(report)
#         self.db.commit()
#         self.db.refresh(report)
#         log_action(
#             event_name="generate_report",
#             metadata={"report_id": str(report.id), "type": report.report_type},
#             tenant_id=self.tenant_id,
#         )
#         return report

#     @log_method_call
#     def archive_report(self, report: Report) -> None:
#         report.is_archived = True
#         self.db.commit()
#         log_action(
#             event_name="archive_report",
#             metadata={"report_id": str(report.id)},
#             tenant_id=self.tenant_id,
#         )
