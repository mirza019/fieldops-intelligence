# Dimensional model and grains

| Table | Grain |
|---|---|
| `DimDate` | One row per calendar date |
| `DimCustomer` | One SCD2 version of a customer |
| `DimRegion` | One governed region |
| `DimTechnician` | One SCD2 version of a technician |
| `DimEquipment` | One SCD2 version of an asset |
| `DimServiceType` | One service type |
| `DimServiceStatus` | One governed status |
| `DimSLAContract` | One version of a contractual SLA |
| `DimDelayReason` | One governed delay reason |
| `FactServiceOrder` | One service order at its current analytical version |
| `FactServiceVisit` | One completed or planned visit for an order |
| `FactTechnicianTime` | One technician time entry for one activity interval |
| `FactServiceCost` | One cost transaction for an order/visit |
| `FactPartsFulfillment` | One requested part line for an order |
| `FactSLAEvent` | One SLA milestone event for an order |
| `FactDataQuality` | One rule result for one record in one pipeline run |
| `FactImprovementAction` | One action within one improvement case |

Order state changes and case transitions are stored as append-only event/history rows with effective timestamps and actor/run IDs. SCD2 is used only for attributes whose historical value affects analysis. Facts are aggregated independently before conformed-dimension comparisons; facts are never directly joined at detail grain.

